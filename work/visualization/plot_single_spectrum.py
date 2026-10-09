"""绘制一个空间点的原始、背景和校正光谱。"""

from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import tifffile
import matplotlib.pyplot as plt
from raman.io import read_tiff

RAW_PATH = Path("input.tif")  # 原始三维 TIFF
BACKGROUND_PATH = Path("work/baseline/output/background.tif")  # 背景 TIFF
CORRECTED_PATH = Path("work/baseline/output/corrected.tif")  # 读取基线步骤已有结果，绘图时不再扣背景
OUTPUT_PATH = Path("work/visualization/output/spectrum.png")  # 图片输出
X, Y = 0, 0  # 要绘制的空间点
READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}  # Raman 位移范围

data = read_tiff(RAW_PATH, **READER_OPTIONS)
background_cube = np.asarray(tifffile.imread(BACKGROUND_PATH), dtype=float)
raw = np.asarray(data.intensity[Y, X], dtype=float)
background = background_cube[Y, X]
corrected_data = read_tiff(CORRECTED_PATH, **READER_OPTIONS)
if corrected_data.intensity.shape != data.intensity.shape or not np.allclose(corrected_data.spectral_axis, data.spectral_axis):
    raise ValueError("原始谱与校正谱必须具有一致的立方体形状和位移轴")
corrected = np.asarray(corrected_data.intensity[Y, X], dtype=float)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
figure, axis = plt.subplots(figsize=(8, 4.5))
axis.plot(data.spectral_axis, raw, label="raw")
axis.plot(data.spectral_axis, background, label="background")
axis.plot(data.spectral_axis, corrected, label="corrected")
axis.set(xlabel="Raman shift", ylabel="Intensity", title=f"x={X}, y={Y}")
axis.legend()
figure.tight_layout()
figure.savefig(OUTPUT_PATH, dpi=150)
plt.close(figure)
print(f"已保存图片：{OUTPUT_PATH}")
