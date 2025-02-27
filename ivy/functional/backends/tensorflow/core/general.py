"""
Collection of TensorFlow general functions, wrapped to fit Ivy syntax and signature.
"""

# global
import ivy
_round = round
import numpy as _np
import math as _math
import tensorflow as _tf
from numbers import Number
import tensorflow_probability as _tfp
import multiprocessing as _multiprocessing
from tensorflow.python.types.core import Tensor

# local
from ivy.functional.ivy.core import default_device, default_dtype
from ivy.functional.backends.tensorflow.core.device import _dev_callable, dev_from_str

DTYPE_TO_STR = {_tf.int8: 'int8',
                _tf.int16: 'int16',
                _tf.int32: 'int32',
                _tf.int64: 'int64',
                _tf.uint8: 'uint8',
                _tf.uint16: 'uint16',
                _tf.uint32: 'uint32',
                _tf.uint64: 'uint64',
                _tf.bfloat16: 'bfloat16',
                _tf.float16: 'float16',
                _tf.float32: 'float32',
                _tf.float64: 'float64',
                _tf.bool: 'bool'}

DTYPE_FROM_STR = {'int8': _tf.int8,
                'int16': _tf.int16,
                'int32': _tf.int32,
                'int64': _tf.int64,
                'uint8': _tf.uint8,
                'uint16': _tf.uint16,
                'uint32': _tf.uint32,
                'uint64': _tf.uint64,
                'bfloat16': _tf.bfloat16,
                'float16': _tf.float16,
                'float32': _tf.float32,
                'float64': _tf.float64,
                'bool': _tf.bool}


# API #
# ----#

# noinspection PyShadowingNames
def array(object_in, dtype=None, dev=None):
    dtype = dtype_from_str(default_dtype(dtype, object_in))
    dev = default_device(dev)
    with _tf.device(dev_from_str(dev)):
        try:
            tensor = _tf.convert_to_tensor(object_in, dtype=dtype)
        except (TypeError, ValueError):
            tensor = _tf.convert_to_tensor(ivy.nested_map(object_in, lambda x: _tf.cast(x, dtype)), dtype=dtype)
        if dtype is None:
            return tensor
        return _tf.cast(tensor, dtype)


asarray = array


def is_array(x, exclusive=False):
    if isinstance(x, Tensor):
        if exclusive and isinstance(x, _tf.Variable):
            return False
        return True
    return False


copy_array = _tf.identity
array_equal = _tf.experimental.numpy.array_equal


def dtype_bits(dtype_in):
    dtype_str = dtype_to_str(dtype_in)
    if 'bool' in dtype_str:
        return 1
    return int(dtype_str.replace('tf.', '').replace('uint', '').replace('int', '').replace('bfloat', '').replace(
        'float', ''))


def equal(x1, x2):
    x1_bits = dtype_bits(x1.dtype)
    if isinstance(x2, (int, float, bool)):
        return x1 == x2
    x2_bits = dtype_bits(x2.dtype)
    if x1_bits > x2_bits:
        x2 = _tf.cast(x2, x1.dtype)
    elif x2_bits > x1_bits:
        x1 = _tf.cast(x1, x2.dtype)
    return x1 == x2


to_numpy = lambda x: _np.asarray(_tf.convert_to_tensor(x))
to_numpy.__name__ = 'to_numpy'
to_scalar = lambda x: to_numpy(x).item()
to_scalar.__name__ = 'to_scalar'
to_list = lambda x: x.numpy().tolist()
to_list.__name__ = 'to_list'
shape = lambda x, as_tensor=False: _tf.shape(x) if as_tensor else tuple(x.shape)
shape.__name__ = 'shape'
get_num_dims = lambda x, as_tensor=False: _tf.shape(_tf.shape(x))[0] if as_tensor else int(_tf.shape(_tf.shape(x)))
minimum = _tf.minimum
maximum = _tf.maximum
clip = _tf.clip_by_value
# noinspection PyShadowingBuiltins
round = _tf.round
floormod = lambda x, y: x % y
floor = _tf.floor
ceil = _tf.math.ceil



# noinspection PyShadowingBuiltins
def abs(x):
    if 'uint' in dtype(x, as_str=True):
        return x
    return _tf.abs(x)


def argmax(x, axis=0):
    ret = _tf.argmax(x, axis)
    if ret.shape == ():
        return _tf.reshape(ret, (-1,))
    return ret


def argmin(x, axis=0):
    ret = _tf.argmin(x, axis)
    if ret.shape == ():
        return _tf.reshape(ret, (-1,))
    return ret


def cast(x, dtype):
    return _tf.cast(x, dtype_from_str(dtype))


astype = cast


# noinspection PyShadowingNames
def arange(stop, start=0, step=1, dtype=None, dev=None):
    dtype = _tf.__dict__[dtype] if dtype else dtype
    dev = default_device(dev)
    with _tf.device(dev_from_str(dev)):
        return _tf.range(start, stop, delta=step, dtype=dtype)


def linspace(start, stop, num, axis=None, dev=None):
    if axis is None:
        axis = -1
    dev = default_device(dev)
    with _tf.device(ivy.dev_from_str(dev)):
        return _tf.linspace(start, stop, num, axis=axis)


def logspace(start, stop, num, base=10., axis=None, dev=None):
    power_seq = linspace(start, stop, num, axis, default_device(dev))
    return base ** power_seq


def concatenate(xs, axis=-1):
    if xs[0].shape == ():
        return _tf.concat([_tf.expand_dims(x, 0) for x in xs], axis)
    return _tf.concat(xs, axis)


stack = _tf.stack


def unstack(x, axis, keepdims=False):
    if x.shape == ():
        return [x]
    ret = _tf.unstack(x, axis=axis)
    if keepdims:
        return [_tf.expand_dims(r, axis) for r in ret]
    return ret


def split(x, num_or_size_splits=None, axis=0, with_remainder=False):
    if x.shape == ():
        if num_or_size_splits is not None and num_or_size_splits != 1:
            raise Exception('input array had no shape, but num_sections specified was {}'.format(num_or_size_splits))
        return [x]
    if num_or_size_splits is None:
        dim_size = _tf.shape(x)[axis]
        num_or_size_splits = dim_size
    elif isinstance(num_or_size_splits, int) and with_remainder:
        num_chunks = x.shape[axis] / num_or_size_splits
        num_chunks_int = _math.floor(num_chunks)
        remainder = num_chunks - num_chunks_int
        if remainder != 0:
            num_or_size_splits = [num_or_size_splits]*num_chunks_int + [int(remainder*num_or_size_splits)]
    return _tf.split(x, num_or_size_splits, axis)


repeat = _tf.repeat


def tile(x, reps):
    if x.shape == ():
        x = _tf.reshape(x, (-1,))
    if isinstance(reps, Number):
        reps = [reps]
    if isinstance(reps, Tensor) and reps.shape == ():
        reps = _tf.reshape(reps, (-1,))
    return _tf.tile(x, reps)


def constant_pad(x, pad_width, value=0):
    if x.shape == ():
        x = _tf.reshape(x, (-1,))
    return _tf.pad(x, pad_width, constant_values=value)


def zero_pad(x, pad_width):
    if x.shape == ():
        x = _tf.reshape(x, (-1,))
    return _tf.pad(x, pad_width)


def swapaxes(x, axis0, axis1):
    x_shape = x.shape
    num_dims = len(x_shape)
    axis0 %= num_dims
    axis1 %= num_dims
    config = list(range(num_dims))
    config.pop(axis0)
    config.insert(axis0, axis1)
    config.pop(axis1)
    config.insert(axis1, axis0)
    return _tf.transpose(x, config)


transpose = _tf.transpose
expand_dims = _tf.expand_dims
where = lambda condition, x1, x2: _tf.where(_tf.cast(condition, _tf.bool), x1, x2)
indices_where = _tf.where


def isinf(x):
    if ivy.is_int_dtype(x):
        return _tf.zeros_like(x, _tf.bool)
    return _tf.math.is_inf(x)



def isfinite(x):
    if ivy.is_int_dtype(x):
        return _tf.ones_like(x, _tf.bool)
    return _tf.math.is_finite(x)



reshape = lambda x, newshape: _tf.reshape(x, (newshape,) if isinstance(newshape, int) else newshape)
broadcast_to = _tf.broadcast_to


def squeeze(x, axis=None):
    if x.shape == ():
        if axis is None or axis == 0 or axis == -1:
            return x
        raise Exception('tried to squeeze a zero-dimensional input by axis {}'.format(axis))
    return _tf.squeeze(x, axis)




# noinspection PyShadowingNames
def zeros_like(x, dtype=None, dev=None):
    dtype = _tf.__dict__[dtype] if dtype else dtype
    dev = default_device(dev)
    with _tf.device(dev_from_str(dev)):
        return _tf.zeros_like(x, dtype=dtype)


def full(shape, fill_value, dtype=None, device=None):
    with _tf.device(dev_from_str(default_device(device))):
        return _tf.fill(shape, _tf.constant(fill_value, dtype=dtype_from_str(default_dtype(dtype, fill_value))))


# noinspection PyShadowingNames
def ones_like(x, dtype=None, dev=None):
    dtype = _tf.__dict__[dtype] if dtype else dtype
    dev = default_device(dev)
    with _tf.device(dev_from_str(dev)):
        return _tf.ones_like(x, dtype=dtype)


def one_hot(indices, depth, dev=None):
    dev = default_device(dev)
    if dev is not None:
        with _tf.device(dev_from_str(dev)):
            return _tf.one_hot(indices, depth)
    return _tf.one_hot(indices, depth)


cross = _tf.linalg.cross


def matmul(x1, x2):
    # ToDo: add support for other input corner cases, like those explained in torch.matmul() docs
    x1_padded = False
    if len(x1.shape) == 1:
        x1 = _tf.expand_dims(x1, 0)
        x1_padded = True
    ret = _tf.matmul(x1, x2)
    if x1_padded:
        return ret[0]
    return ret


cumsum = _tf.cumsum
cumprod = _tf.math.cumprod


# noinspection PyShadowingNames
def identity(n, dtype='float32', batch_shape=None, dev=None):
    dtype = _tf.__dict__[dtype]
    dev = default_device(dev)
    with _tf.device(dev_from_str(dev)):
        return _tf.eye(n, n, batch_shape=batch_shape, dtype=dtype)


meshgrid = lambda *xs, indexing='ij': _tf.meshgrid(*xs, indexing=indexing)


# noinspection PyShadowingNames
def scatter_flat(indices, updates, size=None, tensor=None, reduction='sum', dev=None):
    target = tensor
    target_given = ivy.exists(target)
    if ivy.exists(size) and ivy.exists(target):
        assert len(target.shape) == 1 and target.shape[0] == size
    if dev is None:
        dev = _dev_callable(updates)
    dtype = updates.dtype
    if reduction == 'sum':
        if target_given:
            return _tf.tensor_scatter_nd_add(tensor, _tf.expand_dims(indices, -1), updates)
        return _tf.scatter_nd(_tf.expand_dims(indices, -1), updates, [size])
    elif reduction == 'min':
        if not target_given:
            target = _tf.fill([size], _tf.cast(1e12, dtype))
        res = _tf.tensor_scatter_nd_min(target, _tf.expand_dims(indices, -1), updates)
        if not target_given:
            res = _tf.where(res == 1e12, 0., res)
    elif reduction == 'max':
        if not target_given:
            target = _tf.fill([size], _tf.cast(-1e12, dtype))
        res = _tf.tensor_scatter_nd_max(target, _tf.expand_dims(indices, -1), updates)
        if not target_given:
            res = _tf.where(res == -1e12, 0., res)
    elif reduction == 'replace':
        if target_given:
            res = _tf.tensor_scatter_nd_update(tensor, _tf.expand_dims(indices, -1), updates)
        else:
            res = _tf.tensor_scatter_nd_update(_tf.zeros([size]), _tf.expand_dims(indices, -1), updates)
    else:
        raise Exception('reduction is {}, but it must be one of "sum", "min" or "max"'.format(reduction))
    with _tf.device(dev_from_str(dev)):
        return res


# noinspection PyShadowingNames
def scatter_nd(indices, updates, shape=None, tensor=None, reduction='sum', dev=None):
    target = tensor
    target_given = ivy.exists(target)
    if ivy.exists(shape) and ivy.exists(target):
        assert ivy.shape_to_tuple(target.shape) == ivy.shape_to_tuple(shape)
    if dev is None:
        dev = _dev_callable(updates)
    shape = list(shape) if ivy.exists(shape) else list(tensor.shape)
    dtype = updates.dtype
    if reduction == 'sum':
        if target_given:
            return _tf.tensor_scatter_nd_add(tensor, indices, updates)
        return _tf.scatter_nd(indices, updates, shape)
    elif reduction == 'min':
        if not target_given:
            target = _tf.fill(shape, _tf.cast(1e12, dtype))
        res = _tf.tensor_scatter_nd_min(target, indices, updates)
        if not target_given:
            res = _tf.where(res == 1e12, 0., res)
    elif reduction == 'max':
        if not target_given:
            target = _tf.fill(shape, _tf.cast(-1e12, dtype))
        res = _tf.tensor_scatter_nd_max(target, indices, updates)
        if not target_given:
            res = _tf.where(res == -1e12, 0., res)
    elif reduction == 'replace':
        if target_given:
            res = _tf.tensor_scatter_nd_update(tensor, indices, updates)
        else:
            res = _tf.tensor_scatter_nd_update(_tf.zeros(shape), indices, updates)
    else:
        raise Exception('reduction is {}, but it must be one of "sum", "min" or "max"'.format(reduction))
    with _tf.device(dev_from_str(dev)):
        return res


def gather(params, indices, axis=-1, dev=None):
    axis = axis % len(indices.shape)
    if dev is None:
        dev = _dev_callable(params)
    with _tf.device(dev_from_str(dev)):
        return _tf.gather(params, indices, axis=axis, batch_dims=axis)


def gather_nd(params, indices, dev=None):
    if dev is None:
        dev = _dev_callable(params)
    with _tf.device(dev_from_str(dev)):
        return _tf.gather_nd(params, indices)


def linear_resample(x, num_samples, axis=-1):
    x_shape = list(x.shape)
    num_x_dims = len(x_shape)
    axis = axis % num_x_dims
    num_vals = x.shape[axis]
    x_post_shape = x_shape[axis+1:]
    xp = _tf.range(num_vals, dtype=_tf.float32)
    x_coords = _tf.range(num_samples, dtype=_tf.float32) * ((num_vals-1)/(num_samples-1))
    x_coords = x_coords + xp[0:1]
    return _tfp.math.interp_regular_1d_grid(x_coords, 0, num_vals-1, x, axis=axis)


def dtype(x, as_str=False):
    dt = x.dtype
    if as_str:
        return dtype_to_str(dt)
    return dt


def dtype_to_str(dtype_in):
    if isinstance(dtype_in, str):
        return dtype_in
    return DTYPE_TO_STR[dtype_in]


def dtype_from_str(dtype_in):
    if not isinstance(dtype_in, str):
        return dtype_in
    return DTYPE_FROM_STR[dtype_in]


compile = lambda fn, dynamic=True, example_inputs=None, static_argnums=None, static_argnames=None: _tf.function(fn)
current_framework_str = lambda: 'tensorflow'
current_framework_str.__name__ = 'current_framework_str'
multiprocessing = lambda context=None: _multiprocessing if context is None else _multiprocessing.get_context(context)
container_types = lambda: []


def inplace_update(x, val):
    if ivy.is_variable(x):
        x.assign(val)
        return x
    raise Exception('TensorFlow does not support inplace operations on non-Variable tensors')


def inplace_decrement(x, val):
    if ivy.is_variable(x):
        x.assign(x - val)
        return x
    raise Exception('TensorFlow does not support inplace operations on non-Variable tensors')


def inplace_increment(x, val):
    if ivy.is_variable(x):
        x.assign(x + val)
        return x
    raise Exception('TensorFlow does not support inplace operations on non-Variable tensors')


inplace_arrays_supported = lambda: False
inplace_variables_supported = lambda: True
