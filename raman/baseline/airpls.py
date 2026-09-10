"""自适应迭代加权惩罚最小二乘（airPLS）基线矫正。"""

from __future__ import annotations

import numpy as np

from ._validation import validate_spectrum


def correct(
    x: np.ndarray,
    y: np.ndarray,
    *,
    lam: float = 1e6,
    diff_order: int = 2,
    max_iter: int = 50,
) -> tuple[np.ndarray, np.ndarray]:
    """返回基线矫正后的信号和 airPLS 估计基线。"""
    _, signal = validate_spectrum(x, y)
    from pybaselines.whittaker import airpls

    baseline, _ = airpls(signal, lam=lam, diff_order=diff_order, max_iter=max_iter)
    return signal - baseline, baseline
