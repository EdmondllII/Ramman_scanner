"""评估当前混合拟合结果，并输出可复核的残差与诊断指标。"""

from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import lmfit
from lmfit.minimizer import reduce_chisquare

from raman.io import read_tiff
from raman.reconstruction import reconstruct_lopc, reconstruct_lorentzian


SPECTRUM_PATH = Path("work/baseline/output/corrected.tif")  # 已完成基线校正的光谱立方体
PARAMETERS_PATH = Path("work/fitting/output/fit_parameters_lopc.csv")  # 当前混合拟合参数
OUTPUT_DIR = Path("work/evaluation/output")  # 评估结果目录
X_COORDINATE, Y_COORDINATE = 0, 0  # 当前评估的空间点
LOPC_RANGE = (720.0, 750.0)  # 必须与 fitting/fit_scan.py 使用的窗口一致
READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}


def _metric_block(target: np.ndarray, fitted: np.ndarray, nvarys: int) -> dict[str, float | int | None]:
    """用 lmfit 相同的残差平方和定义计算一组可比较指标。"""
    target_values = np.asarray(target, dtype=float)
    fitted_values = np.asarray(fitted, dtype=float)
    valid = np.isfinite(target_values) & np.isfinite(fitted_values)
    target_values = target_values[valid]
    fitted_values = fitted_values[valid]
    if target_values.size == 0:
        raise ValueError("评估区间没有有限数据")

    residual = target_values - fitted_values
    chisqr = float(reduce_chisquare(residual))  # lmfit 的 reduce_chisquare 就是 sum(residual**2)
    ndata = int(residual.size)
    nfree = max(1, ndata - int(nvarys))
    redchi = chisqr / nfree
    total_sum = float(reduce_chisquare(target_values - target_values.mean()))
    normalized = chisqr / total_sum if total_sum > np.finfo(float).tiny else None
    rsquared = 1.0 - normalized if normalized is not None else None

    # 这里沿用 lmfit.MinimizerResult 的高斯残差 AIC/BIC 定义；参数表没有保存原始 ModelResult。
    likelihood_term = ndata * np.log(max(chisqr / ndata, np.finfo(float).tiny))
    aic = float(likelihood_term + 2.0 * int(nvarys))
    bic = float(likelihood_term + np.log(ndata) * int(nvarys))
    return {
        "valid_points": ndata,
        "nvarys": int(nvarys),
        "nfree": int(nfree),
        "chisqr": chisqr,
        "redchi": float(redchi),
        "rmse": float(np.sqrt(np.mean(residual**2))),
        "mae": float(np.mean(np.abs(residual))),
        "max_abs_residual": float(np.max(np.abs(residual))),
        "normalized_chisqr": normalized,
        "rsquared": rsquared,
        "aic": aic,
        "bic": bic,
    }


def _read_parameter_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"拟合参数表为空：{path}")
    selected = []
    for row in rows:
        if (np.isclose(float(row["x"]), X_COORDINATE)
                and np.isclose(float(row["y"]), Y_COORDINATE)):
            selected.append(row)
    if not selected:
        raise ValueError(f"参数表中没有空间点 ({X_COORDINATE}, {Y_COORDINATE})")
    return selected


def _reconstruct_components(
    shifts: np.ndarray,
    rows: list[dict[str, str]],
) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
    lorentzian_sum = np.zeros_like(shifts, dtype=float)
    lopc_sum = np.zeros_like(shifts, dtype=float)
    details: list[dict[str, object]] = []
    for row in rows:
        model_name = row["model"].strip().lower()
        if model_name == "lopc":
            component = reconstruct_lopc(
                shifts,
                amplitude=float(row["amplitude"]),
                omega_p=float(row["omega_p"]),
                gamma_p=float(row["gamma_p"]),
                gamma_ph=float(row["gamma_ph"]),
                omega_l=float(row["omega_l"]),
                omega_t=float(row["omega_t"]),
                epsilon_inf=float(row["epsilon_inf"]),
            )
            lopc_sum += component
            position = float(row["position"])
            width = None
        elif model_name == "lorentzian":
            component = reconstruct_lorentzian(
                shifts,
                center=float(row["position"]),
                amplitude=float(row["amplitude"]),
                sigma=float(row["sigma"]),
            )
            lorentzian_sum += component
            position = float(row["position"])
            width = float(row["sigma"])
        else:
            raise ValueError(f"不支持的拟合模型：{row['model']}")

        details.append({
            "peak_id": int(float(row["peak_id"])),
            "model": model_name,
            "position": position,
            "amplitude": float(row["amplitude"]),
            "width_sigma": width,
            "component_max": float(np.nanmax(component)),
        })
    return lorentzian_sum, lopc_sum, details


def _candidate_attributions(details: list[dict[str, object]]) -> list[dict[str, object]]:
    """把文献常见带宽作为候选标签，不把标签当作自动鉴定结论。"""
    bands = [
        ("A1(TO) candidate", (530.0, 535.0)),
        ("E1(TO) candidate", (556.0, 562.0)),
        ("E2(high) candidate", (564.0, 570.0)),
        ("A1(LO)/LOPC candidate", (720.0, 750.0)),
        ("E1(LO) candidate", (739.0, 746.0)),
    ]
    result = []
    for name, (low, high) in bands:
        candidates = [item for item in details if low <= float(item["position"]) <= high]
        result.append({
            "label": name,
            "range_cm-1": [low, high],
            "matches": candidates,
            "status": "candidate_only" if candidates else "not_detected",
        })
    return result


def main() -> None:
    data = read_tiff(SPECTRUM_PATH, **READER_OPTIONS)
    if data.kind != "cube" or data.spectral_axis is None:
        raise ValueError("评估输入必须是三维校正光谱 TIFF")
    cube = np.asarray(data.intensity, dtype=float)
    if not (0 <= Y_COORDINATE < cube.shape[0] and 0 <= X_COORDINATE < cube.shape[1]):
        raise IndexError(f"空间点超出范围：({X_COORDINATE}, {Y_COORDINATE})，数据形状为 {cube.shape[:2]}")

    shifts = np.asarray(data.spectral_axis, dtype=float)
    target = np.asarray(cube[Y_COORDINATE, X_COORDINATE], dtype=float)
    rows = _read_parameter_rows(PARAMETERS_PATH)
    lorentzian_sum, lopc_sum, details = _reconstruct_components(shifts, rows)
    fitted_sum = lorentzian_sum + lopc_sum

    finite = np.isfinite(shifts) & np.isfinite(target) & np.isfinite(fitted_sum)
    if finite.sum() < 3:
        raise ValueError("有效评估点至少需要三个")
    shifts = shifts[finite]
    target = target[finite]
    lorentzian_sum = lorentzian_sum[finite]
    lopc_sum = lopc_sum[finite]
    fitted_sum = fitted_sum[finite]
    outside_lopc = (shifts < LOPC_RANGE[0]) | (shifts > LOPC_RANGE[1])
    inside_lopc = ~outside_lopc

    lorentzian_count = sum(item["model"] == "lorentzian" for item in details)
    lopc_count = sum(item["model"] == "lopc" for item in details)
    effective_nvarys = 3 * lorentzian_count + 5 * lopc_count
    metrics = {
        "full_reconstructed_sum": _metric_block(target, fitted_sum, effective_nvarys),
        "lorentzian_objective_outside_lopc": _metric_block(
            target[outside_lopc], lorentzian_sum[outside_lopc], 3 * lorentzian_count
        ),
        "lopc_objective_inside_lopc": _metric_block(
            target[inside_lopc], lopc_sum[inside_lopc], 5 * lopc_count
        ),
        "total_sum_inside_lopc": _metric_block(
            target[inside_lopc], fitted_sum[inside_lopc], effective_nvarys
        ),
    }

    spacing = float(np.median(np.diff(shifts)))
    negative_amplitudes = [item for item in details if float(item["amplitude"]) < 0]
    broad_components = [
        item for item in details
        if item["model"] == "lorentzian" and float(item["width_sigma"]) > 10.0
    ]
    sorted_positions = sorted(details, key=lambda item: float(item["position"]))
    near_duplicates = []
    for previous, current in zip(sorted_positions, sorted_positions[1:]):
        separation = float(current["position"]) - float(previous["position"])
        if separation < 10.0:
            near_duplicates.append({
                "first_peak_id": previous["peak_id"],
                "second_peak_id": current["peak_id"],
                "separation_cm-1": separation,
            })

    lopc_rows = [row for row in rows if row["model"].strip().lower() == "lopc"]
    lopc_diagnostics = []
    for row in lopc_rows:
        lopc_diagnostics.append({
            "peak_id": int(float(row["peak_id"])),
            "omega_l": float(row["omega_l"]),
            "omega_p": float(row["omega_p"]),
            "gamma_p": float(row["gamma_p"]),
            "gamma_ph": float(row["gamma_ph"]),
            "gamma_p_over_window": float(row["gamma_p"]) / (LOPC_RANGE[1] - LOPC_RANGE[0]),
            "gamma_ph_over_sampling_step": float(row["gamma_ph"]) / spacing,
        })

    metrics_payload = {
        "inputs": {
            "spectrum": str(SPECTRUM_PATH),
            "parameters": str(PARAMETERS_PATH),
            "coordinate": {"x": X_COORDINATE, "y": Y_COORDINATE},
            "lopc_range_cm-1": list(LOPC_RANGE),
            "lmfit_version": getattr(lmfit, "__version__", "unknown"),
        },
        "data": {
            "valid_points": int(shifts.size),
            "sampling_step_cm-1": spacing,
            "component_count": len(details),
            "model_counts": dict(Counter(item["model"] for item in details)),
            "effective_parameter_count": effective_nvarys,
        },
        "metrics": metrics,
        "diagnostics": {
            "negative_amplitude_components": negative_amplitudes,
            "broad_lorentzian_components_sigma_gt_10": broad_components,
            "nearby_component_pairs_within_10_cm-1": near_duplicates,
            "lopc_parameters": lopc_diagnostics,
            "candidate_attributions": _candidate_attributions(details),
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"x{X_COORDINATE}_y{Y_COORDINATE}"
    metrics_path = OUTPUT_DIR / f"fit_metrics_{stem}.json"
    spectrum_path = OUTPUT_DIR / f"fit_spectrum_{stem}.csv"
    report_path = OUTPUT_DIR / f"fit_report_{stem}.txt"
    metrics_path.write_text(
        json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    np.savetxt(
        spectrum_path,
        np.column_stack((shifts, target, fitted_sum, lorentzian_sum, lopc_sum, target - fitted_sum)),
        delimiter=",",
        header="raman_shift,target,fitted_sum,lorentzian_sum,lopc_sum,residual",
        comments="",
    )
    full = metrics["full_reconstructed_sum"]
    objective_l = metrics["lorentzian_objective_outside_lopc"]
    objective_p = metrics["lopc_objective_inside_lopc"]
    report_path.write_text(
        "\n".join([
            f"Current fit evaluation: x={X_COORDINATE}, y={Y_COORDINATE}",
            f"components: {len(details)} ({lorentzian_count} Lorentzian + {lopc_count} LOPC)",
            f"full reconstructed R-squared: {full['rsquared']}",
            f"full reconstructed RMSE: {full['rmse']}",
            f"Lorentzian objective outside LOPC RMSE: {objective_l['rmse']}",
            f"LOPC objective inside LOPC RMSE: {objective_p['rmse']}",
            f"negative amplitude components: {len(negative_amplitudes)}",
            f"broad Lorentzian components (sigma > 10): {len(broad_components)}",
            "",
            "注意：CSV 参数表没有保存 lmfit ModelResult，因此这里不能恢复 covar、nfev、success 或原始 fit_report。",
            "AIC/BIC 与 redchi 按 lmfit 的残差定义重算，且混合模型的两个区间是分开拟合的，应作为诊断而非唯一判据。",
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"已保存评估指标：{metrics_path}")
    print(f"已保存评估光谱：{spectrum_path}")
    print(f"已保存评估报告：{report_path}")


if __name__ == "__main__":
    main()
