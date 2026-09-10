"""非对称最小二乘（AsLS）基线矫正。"""

from __future__ import annotations

import numpy as np

from ._validation import validate_spectrum


def correct(
    x: np.ndarray,
    y: np.ndarray,
    *,
    lam: float = 1e6,
    p: float = 0.01,
    diff_order: int = 2,
    max_iter: int = 50,
) -> tuple[np.ndarray, np.ndarray]:
    """返回基线矫正后的信号和 AsLS 估计基线。"""
    _, signal = validate_spectrum(x, y)
    from pybaselines.whittaker import asls

    baseline, _ = asls(signal, lam=lam, p=p, diff_order=diff_order, max_iter=max_iter)
    return signal - baseline, baseline
