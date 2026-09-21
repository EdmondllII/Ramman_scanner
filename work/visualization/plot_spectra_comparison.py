"""将多条两列 CSV 光谱绘制在同一张图中。"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
from raman.io import read_csv_spectrum

INPUT_PATHS = [
    Path("work/visualization/output/corrected_x0_y0.csv"),
    Path("work/reconstruction/output/reconstructed.csv"),
]  # 第一个为数据，其余为拟合曲线
OUTPUT_PATH = Path("work/visualization/output/comparison.png")  # 图片输出

figure, axis = plt.subplots(figsize=(8, 4.5))
for index, path in enumerate(INPUT_PATHS):
    shifts, intensity = read_csv_spectrum(path)
    if index == 0:
        axis.scatter(shifts, intensity, s=1, color="black", label=path.stem)
    else:
        axis.plot(shifts, intensity, linewidth=0.5, color="red", label=path.stem)
axis.set(xlabel="Raman shift", ylabel="Intensity")
axis.legend()
figure.tight_layout()
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
figure.savefig(OUTPUT_PATH, dpi=150)
plt.close(figure)
print(f"已保存图片：{OUTPUT_PATH}")
