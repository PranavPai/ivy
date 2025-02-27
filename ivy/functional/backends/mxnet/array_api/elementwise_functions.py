# global
import mxnet as mx
import math

# local
from ivy.functional.backends.mxnet import _handle_flat_arrays_in_out


def bitwise_and(x1: mx.ndarray.ndarray.NDArray, x2: mx.ndarray.ndarray.NDArray) -> mx.nd.ndarray.NDArray:
    return mx.numpy.bitwise_and(x1, x2)


@_handle_flat_arrays_in_out
def isfinite(x: mx.ndarray.ndarray.NDArray) \
        -> mx.ndarray.ndarray.NDArray:
    # ToDo: remove float32 conversion once int8 and uint8 work correctly. Currently 0 returns 0 for these types.
    return mx.nd.contrib.isfinite(x.astype('float32')).astype('bool')


def sign(x: mx.ndarray.ndarray.NDArray) \
        -> mx.ndarray.ndarray.NDArray:
    return _mx.nd.contrib.sign(x.astype('float32')).astype(dtype)


def sqrt(x: mx.ndarray.ndarray.NDArray) -> mx.ndarray.ndarray.NDArray:
    if isinstance(x, float):
        return math.sqrt(x)
    return mx.nd.sqrt(x)


@_handle_flat_arrays_in_out
def isnan(x: mx.ndarray.ndarray.NDArray) \
        -> mx.ndarray.ndarray.NDArray:
    return mx.nd.contrib.isnan(x).astype('bool')


@_handle_flat_arrays_in_out
def less(x1: mx.ndarray.ndarray.NDArray, x2: mx.ndarray.ndarray.NDArray) \
        -> mx.ndarray.ndarray.NDArray:
    return mx.nd.lesser(x1, x2).astype('bool')


@_handle_flat_arrays_in_out
def logical_not(x: mx.ndarray.ndarray.NDArray) \
        -> mx.ndarray.ndarray.NDArray:
    return mx.nd.logical_not(x)
