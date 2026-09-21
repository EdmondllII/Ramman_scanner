"""计算目标光谱和拟合光谱的误差指标。"""

from pathlib import Path
import json
import sys

import numpy as np
from lmfit.minimizer import reduce_chisquare

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.io import read_csv_spectrum

TARGET_PATH = Path("target.csv")  # 目标光谱 CSV
FITTED_PATH = Path("fitted.csv")  # 拟合或重建光谱 CSV
OUTPUT_PATH = Path("work/evaluation/output/fit_metrics.json")  # 指标输出
LMFIT_TINY = 1e-15  # 与 lmfit 的 R-squared 计算保持一致

target_x, target_y = read_csv_spectrum(TARGET_PATH)
fitted_x, fitted_y = read_csv_spectrum(FITTED_PATH)
if target_x.shape != fitted_x.shape or not np.allclose(target_x, fitted_x):
    raise ValueError("目标光谱和拟合光谱必须使用相同的 Raman 位移轴")
finite = np.isfinite(target_x) & np.isfinite(target_y) & np.isfinite(fitted_y)
target_x, target_y, fitted_y = target_x[finite], target_y[finite], fitted_y[finite]
if target_x.size < 2:
    raise ValueError("有效光谱点至少需要两个")

residual = target_y - fitted_y
chisqr = float(reduce_chisquare(residual))
target_chisqr = float(reduce_chisquare(target_y - target_y.mean()))
normalized_chisqr = chisqr / max(LMFIT_TINY, target_chisqr)
target_gradient = np.gradient(target_y, target_x)
fitted_gradient = np.gradient(fitted_y, target_x)
gradient_chisqr = float(reduce_chisquare(target_gradient - fitted_gradient))
gradient_target_chisqr = float(reduce_chisquare(target_gradient))
metrics = {
    "valid_points": int(target_x.size), "chisqr": chisqr,
    "normalized_chisqr": normalized_chisqr, "rsquared": 1 - normalized_chisqr,
    "gradient_chisqr": gradient_chisqr,
    "gradient_normalized_chisqr": gradient_chisqr / max(LMFIT_TINY, gradient_target_chisqr),
}
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已保存拟合指标：{OUTPUT_PATH}")
