"""只根据目标光谱和已有拟合光谱计算误差，不接触模型或参数。"""

import numpy as np


def spectrum_metrics(shifts, target, fitted):
    """输入是已对齐、有限且位移严格递增的一维数组。"""
    shifts, target, fitted = (np.asarray(values, dtype=float) for values in (shifts, target, fitted))
    if shifts.ndim != 1 or target.shape != shifts.shape or fitted.shape != shifts.shape:
        raise ValueError("Spectrum arrays must be one-dimensional and have matching shapes")
    if shifts.size < 2 or not np.all(np.isfinite([shifts, target, fitted])):
        raise ValueError("At least two finite spectrum points are required")
    if np.any(np.diff(shifts) <= 0):
        raise ValueError("Raman shifts must be strictly increasing")
    residual = target - fitted
    chisqr = float(np.sum(residual**2))
    total_sum = float(np.sum((target - target.mean())**2))
    gradient = np.gradient(target, shifts)
    gradient_error = gradient - np.gradient(fitted, shifts)
    gradient_chisqr = float(np.sum(gradient_error**2))
    tiny = 1.e-15
    return {
        "valid_points": int(shifts.size),
        "chisqr": chisqr,
        "normalized_chisqr": chisqr / max(tiny, total_sum),
        "rsquared": 1.0 - chisqr / max(tiny, total_sum),
        "rmse": float(np.sqrt(np.mean(residual**2))),
        "mae": float(np.mean(np.abs(residual))),
        "max_abs_residual": float(np.max(np.abs(residual))),
        "gradient_chisqr": gradient_chisqr,
        "gradient_normalized_chisqr": gradient_chisqr / max(tiny, float(np.sum(gradient**2))),
    }
