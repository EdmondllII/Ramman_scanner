"""Gaussian 线型重建。"""

from __future__ import annotations

import numpy as np


def reconstruct(
    x: np.ndarray,
    *,
    center: float,
    amplitude: float,
    sigma: float,
    **_: object,
) -> np.ndarray:
    """按照 lmfit GaussianModel 的 amplitude 定义返回 Gaussian 曲线。

    这里的 ``amplitude`` 表示曲线下的积分面积。
    """
    coordinates = np.asarray(x, dtype=float)
    width = float(sigma)
    if not np.isfinite(width) or width <= 0:
        raise ValueError("sigma must be a positive finite number")
    return float(amplitude) / (width * np.sqrt(2.0 * np.pi)) * np.exp(
        -0.5 * ((coordinates - float(center)) / width) ** 2
    )
