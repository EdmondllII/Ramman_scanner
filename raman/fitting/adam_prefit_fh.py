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


def lopc_fh_convolved_torch(
    x,
    amplitude,
    omega_p,
    gamma_p,
    gamma_ph,
    omega_l,
    omega_t,
    epsilon_inf,
    C,
    sigma_inst,
):
    """用 Torch 计算完整 A 项的 Gaussian 卷积，保留宽度的梯度。"""
    coordinates = torch.as_tensor(x, dtype=torch.float64)
    sigma = torch.as_tensor(sigma_inst, dtype=coordinates.dtype, device=coordinates.device)
    sigma_value = float(sigma.detach().cpu())
    if not np.isfinite(sigma_value) or sigma_value < 0.0:
        raise ValueError("sigma_inst must be finite and non-negative")
    if sigma_value == 0.0:
        return lopc_fh_torch(
            x, amplitude=amplitude, omega_p=omega_p, gamma_p=gamma_p,
            gamma_ph=gamma_ph, omega_l=omega_l, omega_t=omega_t,
            epsilon_inf=epsilon_inf, C=C,
        )
    grid = coordinates.detach().cpu().numpy()
    if grid.ndim != 1 or grid.size < 2 or not np.all(np.isfinite(grid)):
        raise ValueError("Gaussian convolution requires a finite one-dimensional x grid")
    steps = np.diff(grid)
    spacing = float(np.median(steps))
    if np.any(steps <= 0.0) or not np.allclose(steps, spacing, rtol=1.e-6, atol=1.e-10):
        raise ValueError("Gaussian convolution requires a uniform increasing x grid")
    pad = max(1, int(np.ceil(6.0 * sigma_value / spacing)))
    # 网格长度不参与梯度；Gaussian 核中的 sigma 保留梯度。
    extended = torch.as_tensor(
        np.arange(grid[0] - pad * spacing, grid[-1] + (pad + 1) * spacing, spacing),
        dtype=coordinates.dtype,
        device=coordinates.device,
    )
    intrinsic = lopc_fh_torch(
        extended, amplitude=amplitude, omega_p=omega_p, gamma_p=gamma_p,
        gamma_ph=gamma_ph, omega_l=omega_l, omega_t=omega_t,
        epsilon_inf=epsilon_inf, C=C,
    )
    kernel_axis = torch.arange(-pad, pad + 1, dtype=coordinates.dtype,
                               device=coordinates.device) * spacing
    kernel = torch.exp(-0.5 * (kernel_axis / sigma) ** 2)
    kernel = kernel / torch.sum(kernel)
    smoothed = torch.nn.functional.conv1d(
        intrinsic[None, None, :], kernel[None, None, :], padding=pad
    )[0, 0]
    return smoothed[pad:pad + coordinates.numel()]


def _inverse_softplus(value: float) -> float:
    value = max(float(value), _TINY)
    if value > 20.0:
        return value
    return float(np.log(np.expm1(value)))


def _inverse_sigmoid(value: float) -> float:
    value = min(max(float(value), _TINY), 1.0 - _TINY)
    return float(np.log(value / (1.0 - value)))


def _physical_values(raw, layout, initial_values, vary):
    """按统一开关从 Adam 的原始变量恢复物理参数。"""
    values = dict(initial_values)
    cursor = 0

    for name in layout["positive"]:
        values[name] = layout["scales"][name] * torch.nn.functional.softplus(raw[cursor])
        cursor += 1

    if vary["omega_l"]:
        gap = values.get("lo_to_gap")
        values["omega_l"] = values["omega_t"] + gap
    elif vary["omega_t"]:
        # 固定绝对 omega_l；用 sigmoid 保证 0 < omega_t < omega_l。
        values["omega_t"] = values["omega_l"] * torch.sigmoid(raw[cursor])
        cursor += 1

    if vary["C"]:
        values["C"] = raw[cursor]
    return {name: values[name] for name in
            ("amplitude", "omega_p", "gamma_p", "gamma_ph",
             "omega_l", "omega_t", "epsilon_inf", "C", "sigma_inst")
            if name in values}


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
    vary_amplitude: bool = True,
    vary_omega_p: bool = True,
    vary_gamma_p: bool = True,
    vary_gamma_ph: bool = True,
    vary_omega_l: bool = True,
    vary_omega_t: bool = False,
    vary_epsilon_inf: bool = False,
    vary_C: bool = True,
    sigma_inst: float = 0.0,
    vary_sigma_inst: bool = False,
    convolved: bool = False,
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
    initial_values.setdefault("omega_t", float(omega_t))
    initial_values.setdefault("epsilon_inf", float(epsilon_inf))
    if initial_values["omega_l"] <= omega_t:
        raise ValueError("Full A term requires omega_l > omega_t")
    if not np.isfinite(initial_values["C"]):
        raise ValueError("C must be finite")
    if convolved and (not np.isfinite(sigma_inst) or sigma_inst < 0.0):
        raise ValueError("sigma_inst must be finite and non-negative")
    if vary_sigma_inst and (not convolved or sigma_inst <= 0.0):
        raise ValueError("vary_sigma_inst requires convolution and a positive initial sigma_inst")
    if convolved:
        initial_values["sigma_inst"] = float(sigma_inst)
    vary = {
        "amplitude": vary_amplitude, "omega_p": vary_omega_p,
        "gamma_p": vary_gamma_p, "gamma_ph": vary_gamma_ph,
        "omega_l": vary_omega_l, "omega_t": vary_omega_t,
        "epsilon_inf": vary_epsilon_inf, "C": vary_C,
        "sigma_inst": vary_sigma_inst,
    }
    positive_initial = dict(initial_values)
    positive_names = [name for name in
                      ("amplitude", "omega_p", "gamma_p", "gamma_ph")
                      if vary[name]]
    if vary_omega_l and vary_omega_t:
        positive_initial["omega_t"] = initial_values["omega_t"]
        positive_names.append("omega_t")
    if vary_omega_l:
        positive_initial["lo_to_gap"] = initial_values["omega_l"] - omega_t
        positive_names.append("lo_to_gap")
    if vary_epsilon_inf:
        positive_names.append("epsilon_inf")
    if vary_sigma_inst:
        positive_names.append("sigma_inst")
    positive_scales = {
        name: max(abs(float(positive_initial[name])), 1.0e-6)
        for name in positive_names
    }
    raw_values = [_inverse_softplus(positive_initial[name] / positive_scales[name])
                  for name in positive_names]
    if vary_omega_t and not vary_omega_l:
        raw_values.append(_inverse_sigmoid(initial_values["omega_t"] /
                                           initial_values["omega_l"]))
    if vary_C:
        raw_values.append(float(initial_values["C"]))
    raw = torch.tensor(raw_values, dtype=torch.float64, requires_grad=True)
    layout = {"positive": positive_names, "scales": positive_scales}
    y_scale = max(float(np.nanmax(np.abs(y_values[valid]))), 1.0)

    def predict(values):
        if convolved:
            return lopc_fh_convolved_torch(x_tensor, **values)
        return lopc_fh_torch(x_tensor, **values)

    if not raw_values:
        with torch.no_grad():
            fixed_values = _physical_values(raw, layout, initial_values, vary)
            fixed_prediction = predict(fixed_values)
            fixed_loss = torch.mean((weight_tensor * (fixed_prediction - y_tensor) / y_scale) ** 2)
        return {
            **{name: float(value) for name, value in fixed_values.items()},
            "adam_loss": float(fixed_loss),
            "adam_steps": 0.0,
        }
    torch.manual_seed(int(seed))
    optimizer = torch.optim.Adam([raw], lr=float(learning_rate))
    best_loss = float("inf")
    best_raw = raw.detach().clone()
    stale_steps = 0

    for step in range(int(max_steps)):
        optimizer.zero_grad(set_to_none=True)
        values = _physical_values(raw, layout, initial_values, vary)
        predicted = predict(values)
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
        best_values = _physical_values(best_raw, layout, initial_values, vary)
    result = {
        name: float(value.detach().cpu()) if isinstance(value, torch.Tensor) else float(value)
        for name, value in best_values.items()
    }
    result["adam_loss"] = best_loss
    result["adam_steps"] = float(step + 1)
    return result
