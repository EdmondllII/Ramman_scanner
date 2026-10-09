"""完整 A 项的单谱重建接口，只调用公共线型，不依赖拟合模块。"""

import numpy as np

from raman.lineshapes import lopc_fh


def reconstruct(x, *, amplitude, omega_p, gamma_p, gamma_ph, omega_l, omega_t, epsilon_inf, C):
    parameters = dict(amplitude=amplitude, omega_p=omega_p, gamma_p=gamma_p,
                      gamma_ph=gamma_ph, omega_l=omega_l, omega_t=omega_t,
                      epsilon_inf=epsilon_inf, C=C)
    if not all(np.isfinite(value) for value in parameters.values()):
        raise ValueError("LOPC parameters must be finite")
    if amplitude < 0 or omega_p < 0:
        raise ValueError("amplitude and omega_p must be non-negative")
    if any(parameters[name] <= 0 for name in ('gamma_p', 'gamma_ph', 'omega_l', 'omega_t', 'epsilon_inf')):
        raise ValueError("frequencies, damping and epsilon_inf must be positive")
    return lopc_fh(np.asarray(x, dtype=float), **parameters)
