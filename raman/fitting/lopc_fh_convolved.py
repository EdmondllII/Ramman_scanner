"""独立实验模型：完整 Faust–Henry A 项经 Gaussian 仪器响应卷积，C 可拟合。"""

from __future__ import annotations

import numpy as np
from .weighting import validate_weights


_TINY = 1.0e-15

from raman.lineshapes import lopc_fh_convolved


def fit(
    x: np.ndarray,
    y: np.ndarray,
    *,
    centers: np.ndarray | list[float],
    omega_t: float,
    epsilon_inf: float = 9.5,
    omega_p: float | None = None,
    gamma_p: float | None = None,
    gamma_ph: float | None = None,
    vary_centers: bool = True,
    vary_omega_t: bool = False,
    vary_epsilon_inf: bool = False,
    C: float = 0.0,  # Signed coefficient, fitted without bounds.
    vary_C: bool = True,
    optimizer: str = "lm",
    adam_options: dict | None = None,
    weights: np.ndarray | None = None,
    sigma_inst: float = 1.0,
):
    r"""使用 lmfit 拟合经过 Gaussian 仪器响应卷积的完整 A 项 LOPC 线型。

    centers 必须只包含一个初始 LO 频率；omega_t 和 epsilon_inf
    提供 TO 频率与高频介电常数的初值。
    """
    from lmfit import Model  # 将 lopc() 包装成可计算残差并优化参数的模型

    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    weights = validate_weights(weights, y_values)
    valid = np.isfinite(x_values) & np.isfinite(y_values)  # 排除会破坏残差计算的 NaN/Inf
    if valid.sum() < 3:
        raise ValueError("At least three finite spectrum points are required")
    x_values, y_values = x_values[valid], y_values[valid]
    order = np.argsort(x_values)  # 保证窗口内坐标递增
    if weights is not None:
        weights = weights[valid][order]
    x_values, y_values = x_values[order], y_values[order]  # 位移和强度同步排序

    peak_centers = np.asarray(centers, dtype=float)
    if peak_centers.ndim != 1 or peak_centers.size != 1:
        raise ValueError("LOPC fitting requires exactly one initial peak centre")
    if not np.isfinite(peak_centers[0]) or peak_centers[0] <= 0:
        raise ValueError("LOPC peak centre must be a positive finite number")
    if not np.isfinite(omega_t) or omega_t <= 0:
        raise ValueError("omega_t must be a positive finite number")
    if not np.isfinite(epsilon_inf) or epsilon_inf <= 0:
        raise ValueError("epsilon_inf must be a positive finite number")

    if not np.isfinite(sigma_inst) or sigma_inst < 0:
        raise ValueError("sigma_inst must be a finite non-negative number")
    if not np.isfinite(C):
        raise ValueError("C must be finite")
    if peak_centers[0] <= omega_t:
        raise ValueError("Full A term requires initial omega_l > omega_t")

    omega_l0 = float(peak_centers[0])  # 用窗口内唯一检测峰作为 omega_l 初值
    spacing = float(np.median(np.diff(x_values)))  # 估计当前数据的典型采样间隔
    width0 = max(abs(spacing) * 2.0, _TINY)  # 未提供阻尼初值时使用的最低尺度
    omega_p0 = (
        max(abs(omega_l0) * 0.1, width0)  # omega_p 缺省初值约为 omega_l 的 10%
        if omega_p is None
        else float(omega_p)
    )
    gamma_p0 = (
        max(abs(omega_l0) * 0.05, width0)  # gamma_p 缺省初值约为 omega_l 的 5%
        if gamma_p is None
        else float(gamma_p)
    )
    gamma_ph0 = (
        max(abs(omega_l0) * 0.01, width0)  # gamma_ph 缺省初值约为 omega_l 的 1%
        if gamma_ph is None
        else float(gamma_ph)
    )
    for name, value in (
        ("gamma_p", gamma_p0),
        ("gamma_ph", gamma_ph0),
    ):
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a positive finite number")
    if not np.isfinite(omega_p0) or omega_p0 < 0:
        raise ValueError("omega_p must be a non-negative finite number")
    base = lopc_fh_convolved(  # 先用全部初值计算一条未缩放的参考曲线
        x_values,
        omega_p=omega_p0,
        gamma_p=gamma_p0,
        gamma_ph=gamma_ph0,
        omega_l=omega_l0,
        omega_t=float(omega_t),
        epsilon_inf=float(epsilon_inf),
        C=float(C),
        sigma_inst=float(sigma_inst),
    )
    base_max = float(np.nanmax(base)) if np.any(np.isfinite(base)) else 0.0  # 初始理论曲线峰高
    signal_max = max(float(np.nanmax(y_values)), 0.0)  # 窗口内实测峰高
    amplitude0 = signal_max / base_max if base_max > _TINY else 1.0  # 让初始曲线高度接近实测数据

    model = Model(lopc_fh_convolved, independent_vars=["x"], nan_policy="omit")  # x 是自变量，其余函数参数交给 lmfit
    parameters = model.make_params(  # 建立优化参数并写入本轮初值
        amplitude=max(amplitude0, _TINY),
        omega_p=omega_p0,
        gamma_p=max(gamma_p0, _TINY),
        gamma_ph=max(gamma_ph0, _TINY),
        omega_l=omega_l0,
        omega_t=float(omega_t),
        epsilon_inf=float(epsilon_inf),
        C=float(C),
        sigma_inst=float(sigma_inst),
    )
    parameters["amplitude"].set(min=0.0)  # 强度缩放不允许为负，目前没有上限
    parameters["omega_p"].set(min=0.0)  # 等离子频率不允许为负，目前没有上限
    parameters["gamma_p"].set(min=_TINY)  # 载流子阻尼仅设正下界，目前没有上限
    parameters["gamma_ph"].set(min=_TINY)  # 声子阻尼仅设正下界，目前没有上限
    parameters["omega_l"].set(min=_TINY, vary=vary_centers)  # 默认允许 LO 参数从检测峰位继续变化
    parameters["omega_t"].set(min=_TINY, vary=vary_omega_t)  # 当前调用中固定为 533 cm^-1
    parameters["epsilon_inf"].set(min=_TINY, vary=vary_epsilon_inf)  # 当前调用中固定为 9.5
    parameters["sigma_inst"].set(value=float(sigma_inst), min=0.0, vary=False)

    # Physical LO-TO ordering; no artificial frequency window or upper bound.
    parameters.add("lo_to_gap", value=omega_l0 - omega_t, min=1.e-12, vary=vary_centers)
    parameters["omega_l"].set(expr="omega_t + lo_to_gap")
    parameters["C"].set(vary=vary_C)

    if optimizer not in {"lm"}:
        raise ValueError("convolved fitting currently supports optimizer='lm' only")
    result = model.fit(
        y_values,
        parameters,
        x=x_values,
        method="leastsq",
        weights=weights,
    )  # 先由 Adam 提供初值，再由现有 leastsq/LM 做最终精修
    return result
