"""逐点估计并扣除背景，将背景、校正 TIFF 和单点 CSV 保存到 baseline。"""

from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import tifffile
from raman.baseline import asls as BASELINE_METHOD  # 改成 asls 即可更换基线方法
from raman.io import read_tiff  # 改成 read_txt 等即可更换读取方法

INPUT_PATH = Path("E:/Edmon/datas/chipdatas/B144XA04001-230515-NC2176/-26_132_LM532.tif")  # 输入的三维 TIFF 文件
OUTPUT_PATH = Path("work/baseline/output/background.tif")  # 输出的背景 TIFF 文件
CORRECTED_OUTPUT_PATH = Path("work/baseline/output/corrected.tif")  # 输出的校正 TIFF 文件
CORRECTED_CSV_PATH = Path("work/baseline/output/corrected_x0_y0.csv")  # 一个空间点的校正谱
READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}  # Raman 位移范围
BASELINE_OPTIONS = {"lam": 1e6, "diff_order": 2, "max_iter": 50}  # 当前基线方法的参数
Y_START, Y_END = 0, 1  # y 范围；改为 3, 4 就只处理 y=3
X_START, X_END = 0, 1  # x 范围；改为 5, 6 就只处理 x=5
CSV_X_COORDINATE, CSV_Y_COORDINATE = 0, 0  # 要导出的校正谱空间点

data = read_tiff(INPUT_PATH, **READER_OPTIONS)
if data.kind != "cube" or data.spectral_axis is None:
    raise ValueError("输入必须是三维 TIFF 光谱立方体")

cube = np.asarray(data.intensity, dtype=float)
background_cube = np.full_like(cube, np.nan, dtype=float)
y_end = cube.shape[0] if Y_END is None else min(Y_END, cube.shape[0])
x_end = cube.shape[1] if X_END is None else min(X_END, cube.shape[1])

for y in range(Y_START, y_end):  # 修改这里的范围即可选择空间点
    for x in range(X_START, x_end):  # 修改这里的范围即可选择空间点
        spectrum = cube[y, x]
        finite = np.isfinite(spectrum)
        if not finite.any():
            continue
        if not finite.all():
            spectrum = np.interp(
                data.spectral_axis,
                data.spectral_axis[finite],
                spectrum[finite],
            )
        _, background = BASELINE_METHOD(  # 先取得背景，本步骤统一扣除并保存校正谱
            data.spectral_axis,
            spectrum,
            **BASELINE_OPTIONS,
        )
        background_cube[y, x] = background

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
tifffile.imwrite(OUTPUT_PATH, background_cube.astype(np.float32))
print(f"已保存背景：{OUTPUT_PATH}")

corrected_cube = cube - background_cube  # 将背景扣除一次并保存，供 fitting 直接使用
tifffile.imwrite(CORRECTED_OUTPUT_PATH, corrected_cube.astype(np.float32))
print(f"已保存校正光谱：{CORRECTED_OUTPUT_PATH}")

corrected = corrected_cube[CSV_Y_COORDINATE, CSV_X_COORDINATE]
CORRECTED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
np.savetxt(
    CORRECTED_CSV_PATH,
    np.column_stack((data.spectral_axis, corrected)),
    delimiter=",",
    header="raman_shift,intensity",
    comments="",
)
print(f"已保存校正谱：{CORRECTED_CSV_PATH}")
