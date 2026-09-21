"""Voigt 线型重建。"""

from __future__ import annotations

import numpy as np


def reconstruct(
    x: np.ndarray,
    *,
    center: float,
    amplitude: float,
    sigma: float,
    gamma: float | None = None,
    **_: object,
) -> np.ndarray:
    """按照 lmfit VoigtModel 的参数定义返回 Voigt 曲线。"""
    from lmfit.lineshapes import voigt

    width = float(sigma)
    lorentz_width = width if gamma is None else float(gamma)
    if not np.isfinite(width) or width <= 0:
        raise ValueError("sigma 必须是有限正数")
    if not np.isfinite(lorentz_width) or lorentz_width <= 0:
        raise ValueError("gamma 必须是有限正数")
    return voigt(
        np.asarray(x, dtype=float),
        amplitude=float(amplitude),
        center=float(center),
        sigma=width,
        gamma=lorentz_width,
    )
