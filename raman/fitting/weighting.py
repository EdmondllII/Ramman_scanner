"""根据观测强度生成固定的饱和权重。"""

import numpy as np


def saturation_weights(y, *, alpha=4.0, scale=3.0):
    """返回残差乘数 sqrt(1 + alpha * (1 - exp(-max(y, 0) / scale)))。"""
    if not np.isfinite(alpha) or alpha < 0 or not np.isfinite(scale) or scale <= 0:
        raise ValueError("alpha must be non-negative and scale must be positive and finite")
    return np.sqrt(1.0 + alpha * (-np.expm1(-np.maximum(y, 0.0) / scale)))


def validate_weights(weights, y):
    """校验可选残差乘数；调用方随后随数据同步过滤和排序。"""
    if weights is None:
        return None
    values = np.asarray(weights, dtype=float)
    if values.shape != y.shape or not np.all(np.isfinite(values) & (values > 0)):
        raise ValueError("weights must match y and contain positive finite residual multipliers")
    return values
