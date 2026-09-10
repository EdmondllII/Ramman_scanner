"""单条光谱数据整理和峰位置检测。"""

from __future__ import annotations

import numpy as np

from raman.data import RamanData


def spectrum_data(data: RamanData) -> tuple[np.ndarray, np.ndarray]:
    """返回独立一维拉曼光谱的数据。"""
    if data.kind == "spectrum":
        return data.x.copy(), data.intensity.copy()
    raise ValueError(
        "二维强度图或光谱立方体必须按空间点处理，不能缩减为平均光谱。"
    )


def detect_peaks(
    x: np.ndarray,
    y: np.ndarray,
    *,
    prominence: float | None = None,
    distance: int = 3,
) -> np.ndarray:
    """使用 SciPy 局部极大值检测器返回峰位置。"""
    from scipy.signal import find_peaks

    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    valid = np.isfinite(x_values) & np.isfinite(y_values)
    if valid.sum() < 3:
        raise ValueError("At least three finite spectrum points are required")
    x_values, y_values = x_values[valid], y_values[valid]
    order = np.argsort(x_values)
    x_values, y_values = x_values[order], y_values[order]

    if prominence is None:
        dynamic_range = float(np.percentile(y_values, 99) - np.percentile(y_values, 1))
        prominence = 0.02 * dynamic_range
    indexes, _ = find_peaks(y_values, prominence=prominence, distance=distance)
    return x_values[indexes]
