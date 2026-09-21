"""LOPC 介电损耗线型拟合。"""

from __future__ import annotations

import numpy as np


_TINY = 1.0e-15


def lopc(
    x: np.ndarray,
    amplitude: float = 1.0,
    omega_p: float = 1.0,
    gamma_p: float = 1.0,
    gamma_ph: float = 1.0,
    omega_l: float = 1.0,
    omega_t: float = 1.0,
    epsilon_inf: float = 1.0,
) -> np.ndarray:
    r"""返回 \(A_{\mathrm{FH}}=1\) 的 LOPC 介电损耗线型。

    x、omega_p、gamma_p、gamma_ph、omega_l 和 omega_t 必须使用同一
    频率单位；Raman 位移坐标可直接使用，只要所有频率参数也使用该单位。
    """
    coordinates = np.asarray(x, dtype=float)  # Raman 位移直接作为统一频率坐标使用
    frequency = np.where(  # 避免 Drude 项在频率为零时除零
        np.abs(coordinates) < _TINY,
        np.where(coordinates < 0.0, -_TINY, _TINY),
        coordinates,
    )
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        dielectric = float(epsilon_inf) * (  # 复介电函数：声子项与自由载流子 Drude 项相加
            1.0
            + (float(omega_l) ** 2 - float(omega_t) ** 2)
            / (
                float(omega_t) ** 2
                - frequency**2
                - 1j * frequency * float(gamma_ph)
            )
            - float(omega_p) ** 2
            / (frequency * (frequency + 1j * float(gamma_p)))
        )
        values = float(amplitude) * np.imag(-1.0 / dielectric)  # Raman 线型取负逆介电函数的虚部
    return np.asarray(values, dtype=float)


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
    optimizer: str = "lm",
    adam_options: dict | None = None,
):
    r"""使用 lmfit 拟合单条 \(A_1(\mathrm{LO})\) LOPC 线型。

    centers 必须只包含一个初始 LO 频率；omega_t 和 epsilon_inf
    提供 TO 频率与高频介电常数的初值。
    """
    from lmfit import Model  # 将 lopc() 包装成可计算残差并优化参数的模型

    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    valid = np.isfinite(x_values) & np.isfinite(y_values)  # 排除会破坏残差计算的 NaN/Inf
    if valid.sum() < 3:
        raise ValueError("At least three finite spectrum points are required")
    x_values, y_values = x_values[valid], y_values[valid]
    order = np.argsort(x_values)  # 保证窗口内坐标递增
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
    base = lopc(  # 先用全部初值计算一条未缩放的参考曲线
        x_values,
        omega_p=omega_p0,
        gamma_p=gamma_p0,
        gamma_ph=gamma_ph0,
        omega_l=omega_l0,
        omega_t=float(omega_t),
        epsilon_inf=float(epsilon_inf),
    )
    base_max = float(np.nanmax(base)) if np.any(np.isfinite(base)) else 0.0  # 初始理论曲线峰高
    signal_max = max(float(np.nanmax(y_values)), 0.0)  # 窗口内实测峰高
    amplitude0 = signal_max / base_max if base_max > _TINY else 1.0  # 让初始曲线高度接近实测数据

    model = Model(lopc, independent_vars=["x"], nan_policy="omit")  # x 是自变量，其余函数参数交给 lmfit
    parameters = model.make_params(  # 建立优化参数并写入本轮初值
        amplitude=max(amplitude0, _TINY),
        omega_p=omega_p0,
        gamma_p=max(gamma_p0, _TINY),
        gamma_ph=max(gamma_ph0, _TINY),
        omega_l=omega_l0,
        omega_t=float(omega_t),
        epsilon_inf=float(epsilon_inf),
    )
    parameters["amplitude"].set(min=0.0)  # 强度缩放不允许为负，目前没有上限
    parameters["omega_p"].set(min=0.0)  # 等离子频率不允许为负，目前没有上限
    parameters["gamma_p"].set(min=_TINY)  # 载流子阻尼仅设正下界，目前没有上限
    parameters["gamma_ph"].set(min=_TINY)  # 声子阻尼仅设正下界，目前没有上限
    parameters["omega_l"].set(min=_TINY, vary=vary_centers)  # 默认允许 LO 参数从检测峰位继续变化
    parameters["omega_t"].set(min=_TINY, vary=vary_omega_t)  # 当前调用中固定为 533 cm^-1
    parameters["epsilon_inf"].set(min=_TINY, vary=vary_epsilon_inf)  # 当前调用中固定为 9.5

    if optimizer not in {"lm", "adam_then_lm"}:
        raise ValueError("optimizer must be 'lm' or 'adam_then_lm'")
    adam_result = None
    if optimizer == "adam_then_lm":
        from .adam_prefit import adam_prefit_lopc

        try:
            adam_result = adam_prefit_lopc(
                x_values,
                y_values,
                initial_values={
                    name: parameters[name].value
                    for name in ("amplitude", "omega_p", "gamma_p", "gamma_ph", "omega_l")
                },
                omega_t=float(omega_t),
                epsilon_inf=float(epsilon_inf),
                **(adam_options or {}),
            )
        except (ImportError, RuntimeError) as exc:
            # Adam 环境或数值阶段失败时，继续用原始初值执行 LM。
            adam_result = {"error": str(exc)}
        else:
            for name in ("amplitude", "omega_p", "gamma_p", "gamma_ph", "omega_l"):
                parameters[name].set(value=adam_result[name])

    result = model.fit(
        y_values,
        parameters,
        x=x_values,
        method="leastsq",
    )  # 先由 Adam 提供初值，再由现有 leastsq/LM 做最终精修
    result.adam_prefit = adam_result
    return result
