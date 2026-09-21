"""将逐点拟合参数绘制为空间热力图。"""

from pathlib import Path
import csv
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt

PARAMETERS_PATH = Path("work/fitting/output/fit_parameters.csv")  # 拟合参数表
PARAMETER_NAME = "position"  # 要显示的参数列名
OUTPUT_PATH = Path("work/visualization/output/position.png")  # 图片输出

with PARAMETERS_PATH.open(newline="", encoding="utf-8-sig") as stream:
    rows = list(csv.DictReader(stream))
if not rows or PARAMETER_NAME not in rows[0]:
    raise ValueError("参数表为空，或找不到指定参数列")

points = {}
for row in rows:  # 每一行是一个空间点的一个峰
    key = (int(float(row["y"])), int(float(row["x"])))
    points.setdefault(key, []).append(float(row[PARAMETER_NAME]))
y_max = max(y for y, _ in points)
x_max = max(x for _, x in points)
image = np.full((y_max + 1, x_max + 1), np.nan)
for (y, x), values in points.items():  # 同一点有多个峰时取平均值
    image[y, x] = np.mean(values)

figure, axis = plt.subplots(figsize=(6, 5))
image_plot = axis.imshow(image, origin="lower", aspect="auto")
figure.colorbar(image_plot, ax=axis, label=PARAMETER_NAME)
axis.set(xlabel="x", ylabel="y", title=PARAMETER_NAME)
figure.tight_layout()
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
figure.savefig(OUTPUT_PATH, dpi=150)
plt.close(figure)
print(f"已保存图片：{OUTPUT_PATH}")
