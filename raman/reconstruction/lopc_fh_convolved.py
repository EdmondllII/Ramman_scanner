"""完整 A 项 Gaussian 仪器卷积后的单谱重建接口。"""

import numpy as np

from raman.lineshapes import lopc_fh_convolved


def reconstruct(x, *, amplitude, omega_p, gamma_p, gamma_ph, omega_l,
                omega_t, epsilon_inf, C, sigma_inst):
    parameters = dict(amplitude=amplitude, omega_p=omega_p, gamma_p=gamma_p,
                      gamma_ph=gamma_ph, omega_l=omega_l, omega_t=omega_t,
                      epsilon_inf=epsilon_inf, C=C, sigma_inst=sigma_inst)
    if not all(np.isfinite(value) for value in parameters.values()):
        raise ValueError("Convolved LOPC parameters must be finite")
    if amplitude < 0 or omega_p < 0 or sigma_inst < 0:
        raise ValueError("amplitude, omega_p and sigma_inst must be non-negative")
    if any(parameters[name] <= 0 for name in
           ("gamma_p", "gamma_ph", "omega_l", "omega_t", "epsilon_inf")):
        raise ValueError("frequencies, damping and epsilon_inf must be positive")
    return lopc_fh_convolved(np.asarray(x, dtype=float), **parameters)
