"""LOPC 介电损耗线型重建。"""

from __future__ import annotations

import numpy as np

from raman.fitting.lopc import lopc


def reconstruct(
    x: np.ndarray,
    *,
    amplitude: float,
    omega_p: float,
    gamma_p: float,
    gamma_ph: float,
    omega_l: float,
    omega_t: float,
    epsilon_inf: float,
    **_: object,
) -> np.ndarray:
    """根据 LOPC 参数返回单条光谱线型。"""
    parameters = {
        "amplitude": amplitude,
        "omega_p": omega_p,
        "gamma_p": gamma_p,
        "gamma_ph": gamma_ph,
        "omega_l": omega_l,
        "omega_t": omega_t,
        "epsilon_inf": epsilon_inf,
    }
    for name, value in parameters.items():
        if not np.isfinite(float(value)):
            raise ValueError(f"{name} must be finite")
    if float(omega_p) < 0:
        raise ValueError("omega_p must be non-negative")
    if any(float(parameters[name]) <= 0 for name in (
        "gamma_p", "gamma_ph", "omega_l", "omega_t", "epsilon_inf"
    )):
        raise ValueError(
            "gamma_p, gamma_ph, omega_l, omega_t, and epsilon_inf must be "
            "positive"
        )
    return lopc(
        np.asarray(x, dtype=float),
        amplitude=float(amplitude),
        omega_p=float(omega_p),
        gamma_p=float(gamma_p),
        gamma_ph=float(gamma_ph),
        omega_l=float(omega_l),
        omega_t=float(omega_t),
        epsilon_inf=float(epsilon_inf),
    )
