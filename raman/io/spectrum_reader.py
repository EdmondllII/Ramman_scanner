"""读取两列 CSV 光谱文件的通用方法。"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def read_csv_spectrum(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """读取两列光谱，返回 Raman 位移和强度数组。"""
    source = Path(path)
    try:
        values = np.loadtxt(source, delimiter=",", ndmin=2)
    except ValueError:
        values = np.loadtxt(source, delimiter=",", skiprows=1, ndmin=2)
    if values.shape[1] < 2:
        raise ValueError(f"光谱文件至少需要两列：{source}")
    return np.asarray(values[:, 0], dtype=float), np.asarray(values[:, 1], dtype=float)
