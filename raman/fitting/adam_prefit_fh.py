"""完整 A 项的独立 Adam 预优化；C 为有符号的自由参数。"""

from __future__ import annotations

from pathlib import Path
import os
import sys
from typing import Mapping

import numpy as np
from .weighting import validate_weights
from .faust_henry import faust_henry_factor


TORCH_ENV_ROOT = Path(r"D:\Edmon\Miniconda\envs\env1")
TORCH_SITE_PACKAGES = TORCH_ENV_ROOT / "Lib" / "site-packages"
_TORCH_DLL_DIRECTORY = None
torch_library_bin = TORCH_ENV_ROOT / "Library" / "bin"
if hasattr(os, "add_dll_directory") and torch_library_bin.is_dir():
    _TORCH_DLL_DIRECTORY = os.add_dll_directory(str(torch_library_bin))

torch_site_packages = str(TORCH_SITE_PACKAGES)
if TORCH_SITE_PACKAGES.is_dir() and torch_site_packages not in sys.path:
    # Torch lazily imports sympy and other env1 dependencies from torch.optim.
    sys.path.insert(0, torch_site_packages)
try:
    import torch
except ImportError as exc:  # pragma: no cover - depends on the external env1 install
    raise RuntimeError(
        f"Cannot import torch from {TORCH_SITE_PACKAGES}"
    ) from exc


_TINY = 1.0e-15


def lopc_fh_torch(
    x,
    amplitude,
    omega_p,
    gamma_p,
    gamma_ph,
    omega_l,
    omega_t,
    epsilon_inf,
    C,
):
    """用 Torch 计算与 NumPy 版一致的完整 A 项线型。"""
    coordinates = torch.as_tensor(x, dtype=torch.float64)
    tiny = torch.as_tensor(_TINY, dtype=coordinates.dtype, device=coordinates.device)
    frequency = torch.where(
        torch.abs(coordinates) < tiny,
        torch.where(coordinates < 0.0, -tiny, tiny),
        coordinates,
    )

    def as_parameter(value):
        if isinstance(value, torch.Tensor):
            return value.to(dtype=coordinates.dtype, device=coordinates.device)
        return torch.as_tensor(value, dtype=coordinates.dtype, device=coordinates.device)

    amplitude = as_parameter(amplitude)
    omega_p = as_parameter(omega_p)
    gamma_p = as_parameter(gamma_p)
    gamma_ph = as_parameter(gamma_ph)
    omega_l = as_parameter(omega_l)
    omega_t = as_parameter(omega_t)
    epsilon_inf = as_parameter(epsilon_inf)
    dielectric = epsilon_inf * (
        1.0
        + (omega_l**2 - omega_t**2)
        / (omega_t**2 - frequency**2 - 1j * frequency * gamma_ph)
        - omega_p**2 / (frequency * (frequency + 1j * gamma_p))
    )
    factor = faust_henry_factor(frequency, omega_p=omega_p, gamma_p=gamma_p,
        gamma_ph=gamma_ph, omega_l=omega_l, omega_t=omega_t, C=C)
    return factor * amplitude * torch.imag(-1.0 / dielectric)


def _inverse_softplus(value: float) -> float:
    value = max(float(value), _TINY)
    if value > 20.0:
        return value
    return float(np.log(np.expm1(value)))


def _physical_values(raw, positive_scales, omega_t, initial_values, vary_C, vary_centers):
    """正值参数无上限；LO 频率不再绑定到拟合数据窗口。"""
    values = {
        name: positive_scales[name] * torch.nn.functional.softplus(raw[index])
        for index, name in enumerate(positive_scales)
    }
    values["omega_l"] = omega_t + values["omega_l"] if vary_centers else initial_values["omega_l"]
    values["C"] = raw[-1] if vary_C else initial_values["C"]
    return values


def adam_prefit_lopc_fh(
    x: np.ndarray,
    y: np.ndarray,
    *,
    initial_values: Mapping[str, float],
    omega_t: float,
    epsilon_inf: float,
    learning_rate: float = 0.02,
    max_steps: int = 1000,
    patience: int = 150,
    seed: int = 0,
    weights: np.ndarray | None = None,
    vary_C: bool = True,
    vary_centers: bool = True,
) -> dict[str, float]:
    """在现有 LM 前用 Adam 预优化 LOPC 参数并返回物理参数。"""
    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    weights = validate_weights(weights, y_values)
    valid = np.isfinite(x_values) & np.isfinite(y_values)
    if valid.sum() < 3:
        raise ValueError("Adam LOPC prefit requires at least three finite points")
    if learning_rate <= 0.0 or max_steps < 1 or patience < 1:
        raise ValueError("Adam learning_rate, max_steps and patience must be positive")

    x_tensor = torch.as_tensor(x_values[valid], dtype=torch.float64)
    y_tensor = torch.as_tensor(y_values[valid], dtype=torch.float64)
    weight_tensor = 1.0 if weights is None else torch.as_tensor(weights[valid], dtype=torch.float64)
    initial_values = dict(initial_values)
    if initial_values["omega_l"] <= omega_t:
        raise ValueError("Full A term requires omega_l > omega_t")
    if not np.isfinite(initial_values["C"]):
        raise ValueError("C must be finite")
    positive_initial = dict(initial_values)
    positive_initial["omega_l"] -= omega_t
    positive_names = ("amplitude", "omega_p", "gamma_p", "gamma_ph", "omega_l")
    positive_scales = {
        name: max(abs(float(positive_initial[name])), 1.0e-6)
        for name in positive_names
    }
    raw = torch.tensor(
        [
            _inverse_softplus(positive_initial[name] / positive_scales[name])
            for name in positive_names
        ] + [float(initial_values["C"])],
        dtype=torch.float64,
        requires_grad=True,
    )
    torch.manual_seed(int(seed))
    optimizer = torch.optim.Adam([raw], lr=float(learning_rate))
    y_scale = max(float(np.nanmax(np.abs(y_values[valid]))), 1.0)
    best_loss = float("inf")
    best_raw = raw.detach().clone()
    stale_steps = 0

    for step in range(int(max_steps)):
        optimizer.zero_grad(set_to_none=True)
        values = _physical_values(raw, positive_scales, omega_t, initial_values, vary_C, vary_centers)
        predicted = lopc_fh_torch(
            x_tensor,
            omega_t=omega_t,
            epsilon_inf=epsilon_inf,
            **values,
        )
        loss = torch.mean((weight_tensor * (predicted - y_tensor) / y_scale) ** 2)
        if not bool(torch.isfinite(loss)):
            break
        loss_value = float(loss.detach().cpu())
        if loss_value < best_loss:
            best_loss = loss_value
            best_raw = raw.detach().clone()
            stale_steps = 0
        else:
            stale_steps += 1
        loss.backward()
        torch.nn.utils.clip_grad_norm_([raw], max_norm=100.0)
        optimizer.step()
        if stale_steps >= int(patience):
            break

    if not np.isfinite(best_loss):
        raise RuntimeError("Adam LOPC prefit did not produce a finite loss")
    with torch.no_grad():
        best_values = _physical_values(best_raw, positive_scales, omega_t, initial_values, vary_C, vary_centers)
    result = {name: float(value.cpu()) for name, value in best_values.items()}
    result["adam_loss"] = best_loss
    result["adam_steps"] = float(step + 1)
    return result
