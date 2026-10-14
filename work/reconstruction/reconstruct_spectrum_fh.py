from pathlib import Path
import csv, json, sys
import numpy as np
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import tifffile
from raman.io import read_csv_spectrum, read_tiff
from raman.reconstruction import reconstruct_lopc_fh, reconstruct_lorentzian

PARAMETERS_PATH = Path("work/fitting/output/fit_parameters_lopc_fh.csv")
SHIFT_SOURCE_PATH = Path("work/baseline/output/corrected.tif")
OUTPUT_PATH = Path("work/reconstruction/output/reconstructed_fh.tif")
Y_START, Y_END = 0, None
X_START, X_END = 0, None
PEAK_IDS = None
READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}
PARAMETER_MAPPING = {"x":"x","y":"y","peak_id":"peak_id","model":"model","center":"position","amplitude":"amplitude","sigma":"sigma","gamma":"gamma","omega_l":"omega_l","omega_p":"omega_p","gamma_p":"gamma_p","gamma_ph":"gamma_ph","omega_t":"omega_t","epsilon_inf":"epsilon_inf","C":"C"}

def reconstruct_point(shifts, rows):
    spectrum = np.zeros_like(shifts, dtype=float)
    for row in rows:
        if PEAK_IDS is not None and int(float(row[PARAMETER_MAPPING["peak_id"]])) not in PEAK_IDS:
            continue
        model_name = row.get(PARAMETER_MAPPING["model"], "").strip().lower()
        if model_name == "lopc_fh":
            spectrum += reconstruct_lopc_fh(shifts, amplitude=float(row["amplitude"]), omega_p=float(row["omega_p"]), gamma_p=float(row["gamma_p"]), gamma_ph=float(row["gamma_ph"]), omega_l=float(row["omega_l"]), omega_t=float(row["omega_t"]), epsilon_inf=float(row["epsilon_inf"]), C=float(row["C"]))
        elif model_name == "lorentzian":
            gamma_text = row.get(PARAMETER_MAPPING["gamma"], "")
            gamma = None if gamma_text in {"", "nan", "NaN"} else float(gamma_text)
            spectrum += reconstruct_lorentzian(shifts, center=float(row["position"]), amplitude=float(row["amplitude"]), sigma=float(row["sigma"]), gamma=gamma)
        else:
            raise ValueError(f"Unsupported model in full A-term table: {model_name}")
    return spectrum

if SHIFT_SOURCE_PATH.suffix.lower() in {".tif", ".tiff"}:
    data = read_tiff(SHIFT_SOURCE_PATH, **READER_OPTIONS)
    if data.kind != "cube" or data.spectral_axis is None:
        raise ValueError("位移轴来源必须是三维 TIFF 光谱立方体")
    shifts = np.asarray(data.spectral_axis, dtype=float)
    cube_shape = np.asarray(data.intensity).shape
else:
    shifts, _ = read_csv_spectrum(SHIFT_SOURCE_PATH)
    shifts = np.asarray(shifts, dtype=float)
    cube_shape = (1, 1, shifts.size)

with PARAMETERS_PATH.open(newline="", encoding="utf-8-sig") as stream:
    rows = list(csv.DictReader(stream))
if not rows:
    raise ValueError("参数表为空")
ny, nx, _ = cube_shape
y_stop = ny if Y_END is None else min(Y_END, ny)
x_stop = nx if X_END is None else min(X_END, nx)
if not (0 <= Y_START <= y_stop and 0 <= X_START <= x_stop):
    raise ValueError("重建范围超出输入立方体")
grouped = {}
for row in rows:
    x, y = int(float(row["x"])), int(float(row["y"]))
    if Y_START <= y < y_stop and X_START <= x < x_stop:
        grouped.setdefault((y, x), []).append(row)
reconstructed = np.full((ny, nx, shifts.size), np.nan, dtype=np.float32)
selected_count = point_count = 0
for (y, x), point_rows in grouped.items():
    reconstructed[y, x] = reconstruct_point(shifts, point_rows).astype(np.float32)
    selected_count += len(point_rows)
    point_count += 1
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
tifffile.imwrite(OUTPUT_PATH, reconstructed)
metadata = {"dimension_order":["y","x","raman_shift"],"shape":list(reconstructed.shape),"raman_shift_range":[float(shifts[0]),float(shifts[-1])],"processing_range":{"y":[Y_START,y_stop],"x":[X_START,x_stop]},"parameters_file":str(PARAMETERS_PATH),"shift_source":str(SHIFT_SOURCE_PATH),"peak_ids":None if PEAK_IDS is None else sorted(PEAK_IDS),"model":"lopc_fh + lorentzian","reconstructed_points":point_count,"selected_peaks":selected_count}
OUTPUT_PATH.with_suffix(".json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已重建 {selected_count} 个峰、{point_count} 个空间点：{OUTPUT_PATH}")
