"""使用 lmfit 的 VoigtModel 实现多峰 Voigt 拟合。"""

from __future__ import annotations

import numpy as np


def fit(
    x: np.ndarray,
    y: np.ndarray,
    *,
    centers: np.ndarray | list[float],
    sigma: float | None = None,
    gamma: float | None = None,
    vary_centers: bool = True,
):
    """为每个峰建立 Voigt 分量并返回 lmfit 拟合结果。

    ``gamma=None`` 时沿用 lmfit 的默认约束 ``gamma=sigma``；传入数值时，
    ``gamma`` 作为独立的 Lorentzian 半高半宽参与拟合。
    """
    from lmfit.models import VoigtModel

    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    valid = np.isfinite(x_values) & np.isfinite(y_values)
    if valid.sum() < 3:
        raise ValueError("至少需要三个有效光谱点")
    x_values, y_values = x_values[valid], y_values[valid]
    order = np.argsort(x_values)
    x_values, y_values = x_values[order], y_values[order]

    peak_centers = np.asarray(centers, dtype=float)
    if peak_centers.ndim != 1 or peak_centers.size == 0:
        raise ValueError("Voigt 拟合至少需要一个峰中心")

    spacing = np.median(np.diff(x_values))
    initial_sigma = float(sigma) if sigma is not None else max(abs(spacing) * 2, 1e-9)
    model = None
    parameters = None
    for index, center in enumerate(peak_centers, 1):
        prefix = f"p{index}_"
        component = VoigtModel(prefix=prefix)
        model = component if model is None else model + component
        height = max(float(np.interp(center, x_values, y_values)), 0.0)
        component_parameters = component.make_params(
            amplitude=max(height * initial_sigma * np.sqrt(2 * np.pi), 1e-12),
            center=float(center),
            sigma=initial_sigma,
        )
        component_parameters[f"{prefix}amplitude"].set(min=0.0)  # 非负面积保证峰高非负
        component_parameters[f"{prefix}center"].set(vary=vary_centers)
        component_parameters[f"{prefix}sigma"].set(min=1e-12)
        if gamma is not None:
            component_parameters[f"{prefix}gamma"].set(
                value=float(gamma), expr=None, min=1e-12, vary=True
            )
        if parameters is None:
            parameters = component_parameters
        else:
            parameters.update(component_parameters)

    return model.fit(y_values, parameters, x=x_values)
