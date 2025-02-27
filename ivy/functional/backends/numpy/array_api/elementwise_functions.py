# global
import numpy as np
import numpy.array_api as npa


def bitwise_and(x1: np.ndarray,
                x2: np.ndarray) \
        -> np.ndarray:
    return np.bitwise_and(x1, x2)


def sqrt(x: np.ndarray) \
        -> np.ndarray:
    return np.sqrt(x)


def isfinite(x: np.ndarray) \
        -> np.ndarray:
    return np.asarray(npa.isfinite(npa.asarray(x)))


def sign(x: np.ndarray) \
        -> np.ndarray:
    return np.asarray(npa.sign(npa.asarray(x)))


def asinh(x: np.ndarray) \
        -> np.ndarray:
    return np.arcsinh(x)


def cosh(x: np.ndarray) \
        -> np.ndarray:
    return np.asarray(npa.cosh(npa.asarray(x)))


def log2(x: np.ndarray)\
        -> np.ndarray:
    return np.log2(x)


def isnan(x: np.ndarray) \
        -> np.ndarray:
    return np.isnan(x)


def less(x1: np.ndarray, x2: np.ndarray) \
        -> np.ndarray:
    return np.less(x1, x2)


def cos(x: np.ndarray) \
        -> np.ndarray:
    return np.asarray(npa.cos(npa.asarray(x)))


def logical_not(x: np.ndarray) \
        -> np.ndarray:
    return np.logical_not(x)
