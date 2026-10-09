"""根据独立 Gaussian 卷积完整 A 项参数表重建光谱。"""

from pathlib import Path
import csv
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.io import read_csv_spectrum, read_tiff  # 可更换位移轴读取方式
from raman.reconstruction import (
    reconstruct_lopc_fh_convolved,
    reconstruct_lorentzian,
)

PARAMETERS_PATH = Path("work/fitting/output/fit_parameters_lopc_fh_convolved.csv")  # LOPC 混合拟合参数表
SHIFT_SOURCE_PATH = Path("work/baseline/output/corrected.tif")  # 提供 Raman 位移轴的校正 TIFF 或 CSV
OUTPUT_PATH = Path("work/reconstruction/output/reconstructed_fh_convolved.csv")  # 重建光谱输出
X_COORDINATE, Y_COORDINATE = 0, 0  # 要重建的空间点坐标
PEAK_IDS = None  # 改成 {1, 3} 可只重建第 1、3 个峰
READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}  # TIFF 位移范围

PARAMETER_MAPPING = {  # 手动指定参数表中每一列的含义，可使用列名
    "x": "x", "y": "y", "peak_id": "peak_id", "model": "model",  # 坐标、峰编号和模型
    "center": "position", "amplitude": "amplitude", "sigma": "sigma",  # 模型参数
    "gamma": "gamma",  # Voigt 的 Lorentzian 半高半宽，其他线型会忽略
    "omega_l": "omega_l", "omega_p": "omega_p", "gamma_p": "gamma_p",
    "gamma_ph": "gamma_ph", "omega_t": "omega_t", "epsilon_inf": "epsilon_inf", "C": "C",
    "sigma_inst": "sigma_inst",
}

if SHIFT_SOURCE_PATH.suffix.lower() in {".tif", ".tiff"}:
    data = read_tiff(SHIFT_SOURCE_PATH, **READER_OPTIONS)
    shifts = data.spectral_axis
else:
    shifts, _ = read_csv_spectrum(SHIFT_SOURCE_PATH)
if shifts is None:
    raise ValueError("无法读取 Raman 位移轴")

with PARAMETERS_PATH.open(newline="", encoding="utf-8-sig") as stream:
    rows = list(csv.DictReader(stream))  # 参数表需要有表头

reconstructed = np.zeros_like(shifts, dtype=float)
selected_count = 0
for row in rows:  # 每一行对应一个峰
    if not (np.isclose(float(row[PARAMETER_MAPPING["x"]]), X_COORDINATE)
            and np.isclose(float(row[PARAMETER_MAPPING["y"]]), Y_COORDINATE)):
        continue
    peak_id = int(float(row[PARAMETER_MAPPING["peak_id"]]))
    if PEAK_IDS is not None and peak_id not in PEAK_IDS:
        continue
    model_name = row.get(PARAMETER_MAPPING["model"], "").strip().lower()
    if model_name == "lopc_fh_convolved":
        reconstructed += reconstruct_lopc_fh_convolved(
            shifts,
            amplitude=float(row[PARAMETER_MAPPING["amplitude"]]),
            omega_p=float(row[PARAMETER_MAPPING["omega_p"]]),
            gamma_p=float(row[PARAMETER_MAPPING["gamma_p"]]),
            gamma_ph=float(row[PARAMETER_MAPPING["gamma_ph"]]),
            omega_l=float(row[PARAMETER_MAPPING["omega_l"]]),
            omega_t=float(row[PARAMETER_MAPPING["omega_t"]]),
            epsilon_inf=float(row[PARAMETER_MAPPING["epsilon_inf"]]),
            C=float(row[PARAMETER_MAPPING["C"]]),
            sigma_inst=float(row[PARAMETER_MAPPING["sigma_inst"]]),
        )
    elif model_name == "lorentzian":
        gamma_text = row.get(PARAMETER_MAPPING["gamma"], "")
        gamma = None if gamma_text in {"", "nan", "NaN"} else float(gamma_text)
        reconstructed += reconstruct_lorentzian(
            shifts,
            center=float(row[PARAMETER_MAPPING["center"]]),
            amplitude=float(row[PARAMETER_MAPPING["amplitude"]]),
            sigma=float(row[PARAMETER_MAPPING["sigma"]]),
            gamma=gamma,
        )
    else:
        raise ValueError(f"Unsupported model in convolved full A-term table: {model_name}")
    selected_count += 1

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
np.savetxt(
    OUTPUT_PATH,
    np.column_stack((shifts, reconstructed)),
    delimiter=",",
    header="raman_shift,intensity",
    comments="",
)
print(f"已重建 {selected_count} 个峰：{OUTPUT_PATH}")
