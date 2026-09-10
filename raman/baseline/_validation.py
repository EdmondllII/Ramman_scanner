"""基线矫正方法共用的输入校验。"""

from __future__ import annotations

import numpy as np


def validate_spectrum(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """返回有限且按 x 坐标排序的一维光谱数据。"""
    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    if x_values.ndim != 1 or y_values.ndim != 1 or x_values.size != y_values.size:
        raise ValueError("x and y must be one-dimensional arrays of the same length")
    valid = np.isfinite(x_values) & np.isfinite(y_values)
    if valid.sum() < 3:
        raise ValueError("At least three finite spectrum points are required")
    x_values = x_values[valid]
    y_values = y_values[valid]
    order = np.argsort(x_values)
    return x_values[order], y_values[order]
