"""保存拉曼处理结果的辅助函数。"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def save_fit_result(
    output_dir: str | Path,
    x: np.ndarray,
    raw: np.ndarray,
    baseline: np.ndarray,
    corrected: np.ndarray,
    fit_result,
) -> None:
    """将处理后的光谱、拟合曲线和拟合参数保存为文件。"""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    np.savetxt(
        directory / "spectrum.csv",
        np.column_stack((x, raw, baseline, corrected, fit_result.best_fit)),
        delimiter=",",
        header="raman_shift,raw_intensity,baseline,corrected_intensity,fitted_intensity",
        comments="",
    )
    parameter_rows = [
        (name, parameter.value, parameter.stderr if parameter.stderr is not None else np.nan)
        for name, parameter in fit_result.params.items()
    ]
    np.savetxt(
        directory / "fit_parameters.csv",
        np.asarray(parameter_rows, dtype=object),
        fmt="%s",
        delimiter=",",
        header="parameter,value,standard_error",
        comments="",
    )
    (directory / "fit_report.txt").write_text(fit_result.fit_report(), encoding="utf-8")
def save_cube_results(
    output_dir: str | Path,
    data,
    baseline: np.ndarray,
    corrected: np.ndarray,
    fitted: np.ndarray,
    parameters: list[dict[str, float]],
) -> None:
    """保存每个空间点的光谱数组和逐峰拟合参数。"""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        directory / "cube_processed.npz",
        x=data.x,
        y=data.y,
        spectral_axis=data.spectral_axis,
        raw_intensity=data.intensity,
        baseline=baseline,
        corrected_intensity=corrected,
        fitted_intensity=fitted,
    )

    fields = (
        "y_index",
        "x_index",
        "peak_id",
        "position",
        "height",
        "amplitude",
        "sigma",
        "fwhm",
    )
    rows = [[record.get(field, np.nan) for field in fields] for record in parameters]
    table = np.asarray(rows, dtype=float) if rows else np.empty((0, len(fields)))
    np.savetxt(
        directory / "cube_fit_parameters.csv",
        table,
        delimiter=",",
        header=",".join(fields),
        comments="",
    )
