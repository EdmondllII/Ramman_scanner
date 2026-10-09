"""比较目标与已有拟合光谱，输出误差指标；不读取参数、不重建、不归因。"""

from pathlib import Path
import json
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.evaluation import spectrum_metrics
from raman.io import read_csv_spectrum

TARGET_PATH = Path("target.csv")  # 实际用于拟合的目标谱：当前流程为校正谱
FITTED_PATH = Path("fitted.csv")  # reconstruction 已生成的拟合谱
OUTPUT_PATH = Path("work/evaluation/output/fit_metrics.json")


def evaluate_files(target_path, fitted_path, output_dir, stem=None, *, regions=None, metrics_path=None):
    """只比较两条 CSV；regions 为可选位移区间，与模型类型无关。"""
    target_x, target_y = read_csv_spectrum(target_path)
    fitted_x, fitted_y = read_csv_spectrum(fitted_path)
    if target_x.shape != fitted_x.shape or not np.allclose(target_x, fitted_x, equal_nan=True):
        raise ValueError("目标光谱和拟合光谱必须使用相同的 Raman 位移轴")
    finite = np.isfinite(target_x) & np.isfinite(target_y) & np.isfinite(fitted_y)
    shifts, target, fitted = target_x[finite], target_y[finite], fitted_y[finite]
    metrics = {"full_spectrum": spectrum_metrics(shifts, target, fitted)}
    for name, (low, high) in (regions or {}).items():
        mask = (shifts >= low) & (shifts <= high)
        if mask.sum() < 2:
            raise ValueError(f"评估区间 {name} 至少需要两个有效点")
        metrics[name] = spectrum_metrics(shifts[mask], target[mask], fitted[mask])

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{stem}" if stem else ""
    metrics_path = Path(metrics_path) if metrics_path else output_dir / f"fit_metrics{suffix}.json"
    residual_path = output_dir / f"fit_spectrum{suffix}.csv"
    report_path = output_dir / f"fit_report{suffix}.txt"
    payload = {
        "inputs": {"target": str(target_path), "fitted": str(fitted_path), "regions_cm-1": regions or {}},
        "metrics": metrics,
    }
    metrics_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    np.savetxt(residual_path, np.column_stack((shifts, target, fitted, target - fitted)),
               delimiter=",", header="raman_shift,target,fitted,residual", comments="")
    report = [f"target: {target_path}", f"fitted: {fitted_path}"]
    for name, block in metrics.items():
        report.append(f"{name}: RMSE={block['rmse']}, R-squared={block['rsquared']}")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"已保存评估指标：{metrics_path}")
    print(f"已保存残差光谱：{residual_path}")
    print(f"已保存评估报告：{report_path}")
    return payload


def main():
    evaluate_files(TARGET_PATH, FITTED_PATH, OUTPUT_PATH.parent, metrics_path=OUTPUT_PATH)


if __name__ == "__main__":
    main()
