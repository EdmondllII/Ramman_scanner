"""Shared pure LOPC line shapes; no fitting, reconstruction I/O, or optimization.

Full A term: trnit1999_195-220.pdf, printed p.197, equations (3.2)-(3.3).
All frequency parameters use the same unit, cm^-1 in this project.
"""

import numpy as np

_TINY = 1.e-15


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


def faust_henry_factor(x, *, omega_p, gamma_p, gamma_ph, omega_l, omega_t, C):
    """C 为有符号、无量纲的散射系数；物理 LO 分支要求 omega_l > omega_t。"""
    w2 = x**2
    t2, l2, p2 = omega_t**2, omega_l**2, omega_p**2
    delta = p2 * gamma_p * ((t2 - w2)**2 + w2 * gamma_ph**2)
    delta = delta + w2 * gamma_ph * (l2 - t2) * (w2 + gamma_p**2)
    linear = p2 * gamma_p * (t2 - w2) - w2 * gamma_ph * (w2 + gamma_p**2 - p2)
    quadratic = p2 * gamma_p * (l2 - t2)
    quadratic = quadratic + p2 * gamma_ph * (p2 - 2 * w2) + w2 * gamma_ph * (w2 + gamma_p**2)
    return 1 + 2 * C * t2 * linear / delta + C**2 * t2**2 * quadratic / (delta * (l2 - t2))


def lopc_fh(x, amplitude=1.0, omega_p=1.0, gamma_p=1.0, gamma_ph=1.0,
            omega_l=735.0, omega_t=533.0, epsilon_inf=9.5, C=0.0):
    """Full A-term response: amplitude * A_FH * Im(-1/epsilon)."""
    x = np.asarray(x, dtype=float)
    if omega_l <= omega_t:
        raise ValueError("Full A term requires omega_l > omega_t")
    factor = faust_henry_factor(x, omega_p=omega_p, gamma_p=gamma_p,
                               gamma_ph=gamma_ph, omega_l=omega_l, omega_t=omega_t, C=C)
    return factor * lopc(x, amplitude=amplitude, omega_p=omega_p,
        gamma_p=gamma_p, gamma_ph=gamma_ph, omega_l=omega_l, omega_t=omega_t, epsilon_inf=epsilon_inf)


def gaussian_convolve(x, values, sigma_inst):
    """在等间隔 Raman 坐标上施加 Gaussian 仪器响应卷积。"""
    coordinates = np.asarray(x, dtype=float)
    signal = np.asarray(values, dtype=float)
    if coordinates.ndim != 1 or signal.shape != coordinates.shape or coordinates.size < 2:
        raise ValueError("x and values must be one-dimensional arrays with at least two points")
    if not np.all(np.isfinite(coordinates)) or not np.all(np.isfinite(signal)):
        raise ValueError("x and values must be finite")
    if np.any(np.diff(coordinates) <= 0):
        raise ValueError("x must be strictly increasing")
    sigma = float(sigma_inst)
    if not np.isfinite(sigma) or sigma < 0:
        raise ValueError("sigma_inst must be a finite non-negative number")
    if sigma == 0:
        return signal.copy()
    spacing = float(np.median(np.diff(coordinates)))
    if not np.allclose(np.diff(coordinates), spacing, rtol=1e-6, atol=1e-10):
        raise ValueError("Gaussian convolution requires an approximately uniform x grid")
    pad = max(1, int(np.ceil(6.0 * sigma / spacing)))
    extended = np.arange(coordinates[0] - pad * spacing,
                         coordinates[-1] + (pad + 1) * spacing,
                         spacing)
    extended_values = np.interp(extended, coordinates, signal)
    kernel_axis = np.arange(-pad, pad + 1, dtype=float) * spacing
    kernel = np.exp(-0.5 * (kernel_axis / sigma) ** 2)
    kernel /= kernel.sum()
    smoothed = np.convolve(extended_values, kernel, mode="same")
    return np.interp(coordinates, extended, smoothed)


def lopc_fh_convolved(x, amplitude=1.0, omega_p=1.0, gamma_p=1.0, gamma_ph=1.0,
                      omega_l=735.0, omega_t=533.0, epsilon_inf=9.5, C=0.0,
                      sigma_inst=0.0):
    """完整 A 项本征响应经过 Gaussian 仪器响应后的线型。"""
    coordinates = np.asarray(x, dtype=float)
    sigma = float(sigma_inst)
    if sigma == 0:
        return lopc_fh(coordinates, amplitude=amplitude, omega_p=omega_p,
                       gamma_p=gamma_p, gamma_ph=gamma_ph, omega_l=omega_l,
                       omega_t=omega_t, epsilon_inf=epsilon_inf, C=C)
    spacing = float(np.median(np.diff(coordinates)))
    pad = max(1, int(np.ceil(6.0 * sigma / spacing)))
    extended = np.arange(coordinates[0] - pad * spacing,
                         coordinates[-1] + (pad + 1) * spacing,
                         spacing)
    intrinsic = lopc_fh(extended, amplitude=amplitude, omega_p=omega_p,
                        gamma_p=gamma_p, gamma_ph=gamma_ph, omega_l=omega_l,
                        omega_t=omega_t, epsilon_inf=epsilon_inf, C=C)
    return gaussian_convolve(extended, intrinsic, sigma)[pad:pad + coordinates.size]



