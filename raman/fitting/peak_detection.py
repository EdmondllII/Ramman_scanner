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
    """使用 SciPy 返回高度非负的局部极大值位置，不截断输入强度。"""
    from scipy.signal import find_peaks  # 这里只做离散局部极大值检测，不执行曲线拟合

    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    valid = np.isfinite(x_values) & np.isfinite(y_values)  # 同时过滤坐标或强度中的 NaN/Inf
    if valid.sum() < 3:
        raise ValueError("At least three finite spectrum points are required")
    x_values, y_values = x_values[valid], y_values[valid]
    order = np.argsort(x_values)  # find_peaks 按数组顺序工作，先保证 Raman 位移递增
    x_values, y_values = x_values[order], y_values[order]  # 强度必须跟随位移使用同一排序

    if prominence is None:  # 调用者未给绝对阈值时才启用动态阈值
        dynamic_range = float(np.percentile(y_values, 99) - np.percentile(y_values, 1))  # 用分位差降低极端点影响
        prominence = 0.025 * dynamic_range  # 峰突出度至少达到当前谱动态范围的 5%
    indexes, _ = find_peaks(y_values, height=0.0, prominence=prominence, distance=distance)  # distance 的单位是采样点数
    return x_values[indexes]  # 把峰数组下标转换成 Raman 位移，作为后续拟合初值
