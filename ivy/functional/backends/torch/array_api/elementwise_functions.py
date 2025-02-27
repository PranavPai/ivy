# global
import torch


def bitwise_and(x1: torch.Tensor,
                x2: torch.Tensor) \
        -> torch.Tensor:
    return torch.bitwise_and(x1, x2)


def isfinite(x: torch.Tensor) \
        -> torch.Tensor:
    return torch.isfinite(x)


def sign(x: torch.Tensor) \
        -> torch.Tensor:
    return torch.sign(x)


def asinh(x: torch.Tensor) \
        -> torch.Tensor:
    return torch.asinh(x)


def sqrt(x: torch.Tensor) \
        -> torch.Tensor:
    return torch.sqrt(x)


def cosh(x: torch.Tensor) \
        -> torch.Tensor:
    return torch.cosh(x)


def log2(x: torch.Tensor) \
        -> torch.Tensor:
    return torch.log2(x)


def isnan(x: torch.Tensor) \
        -> torch.Tensor:
    return torch.isnan(x)


def less(x1: torch.Tensor, x2: torch.Tensor):
    if hasattr(x1, 'dtype') and hasattr(x2, 'dtype'):
        promoted_type = torch.promote_types(x1.dtype, x2.dtype)
        x1 = x1.to(promoted_type)
        x2 = x2.to(promoted_type)
    return torch.lt(x1, x2)


def cos(x: torch.Tensor) \
        -> torch.Tensor:
    return torch.cos(x)


def logical_not(x: torch.Tensor) \
        -> torch.Tensor:
    return torch.logical_not(x.type(torch.bool))
