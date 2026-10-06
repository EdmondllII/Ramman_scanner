"""使用 lmfit 实现的多峰 Lorentzian 拟合。"""

from __future__ import annotations

import numpy as np


def fit(
    x: np.ndarray,
    y: np.ndarray,
    *,
    centers: np.ndarray | list[float],
    sigma: float | None = None,
    vary_centers: bool = True,
):
    """使用与 lmfit 参数命名兼容的 Lorentzian 分量进行拟合。"""
    from lmfit.models import LorentzianModel  # lmfit 内置面积归一化 Lorentzian 模型

    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    valid = np.isfinite(x_values) & np.isfinite(y_values)  # 清除无法参与残差计算的数据点
    if valid.sum() < 3:
        raise ValueError("At least three finite spectrum points are required")
    x_values, y_values = x_values[valid], y_values[valid]
    order = np.argsort(x_values)  # 后续插值和采样间隔估计都要求有序坐标
    x_values, y_values = x_values[order], y_values[order]  # 位移和强度保持一一对应
    peak_centers = np.asarray(centers, dtype=float)  # detect_peaks 的结果就是各分量中心初值
    if peak_centers.ndim != 1 or peak_centers.size == 0:
        raise ValueError("At least one peak centre is required for Lorentzian fitting")
    spacing = np.median(np.diff(x_values))  # 以中位采样间隔降低非均匀点或异常间隔的影响
    initial_sigma = float(sigma) if sigma is not None else max(abs(spacing) * 2, 1e-9)  # 默认半高半宽初值约两个采样间隔
    model = None  # 后续逐个累加 Lorentzian 分量
    parameters = None  # 汇总所有分量的自由参数
    for index, center in enumerate(peak_centers, 1):
        prefix = f"p{index}_"  # 防止不同峰的 amplitude/center/sigma 参数重名
        component = LorentzianModel(prefix=prefix)  # 单峰参数为 amplitude、center、sigma
        model = component if model is None else model + component  # 总模型是所有峰分量的直接求和
        height = max(float(np.interp(center, x_values, y_values)), 0.0)  # 从检测位置插值得到峰高初值
        component_parameters = component.make_params(
            amplitude=max(height * np.pi * initial_sigma, 1e-12),  # lmfit 的 amplitude 表示积分面积而不是峰高
            center=float(center),  # 峰中心从自动寻峰结果开始迭代
            sigma=initial_sigma,  # lmfit Lorentzian 中 sigma 等于半高半宽
        )
        component_parameters[f"{prefix}amplitude"].set(min=0.0)  # 正宽度下，非负面积保证峰高非负
        component_parameters[f"{prefix}center"].set(vary=vary_centers)  # True 时允许中心偏离寻峰位置
        component_parameters[f"{prefix}sigma"].set(min=1e-12)  # 只限制宽度为正，目前没有上限
        if parameters is None:
            parameters = component_parameters
        else:
            parameters.update(component_parameters)
    return model.fit(y_values, parameters, x=x_values)  # 未指定 method，lmfit 默认以 leastsq/LM 最小化残差平方和
