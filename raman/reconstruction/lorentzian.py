"""Lorentzian 线型重建。"""

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
    """返回面积为 ``amplitude``、半高半宽为 ``sigma`` 的 Lorentzian 曲线。"""
    coordinates = np.asarray(x, dtype=float)
    width = float(sigma)
    if not np.isfinite(width) or width <= 0:
        raise ValueError("sigma must be a positive finite number")
    return float(amplitude) / np.pi * width / (
        (coordinates - float(center)) ** 2 + width**2
    )
