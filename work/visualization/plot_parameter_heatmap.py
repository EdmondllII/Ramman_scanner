"""绘制指定峰的已有参数，不混合不同峰或计算平均值。"""

from pathlib import Path
import csv
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt

PARAMETERS_PATH = Path("work/fitting/output/fit_parameters.csv")
PARAMETER_NAME = "position"  # 要显示的参数列名
PEAK_ID = 1  # 只展示指定峰编号，不将不同峰混合取平均
MODEL_NAME = None  # 可设为 lorentzian、lopc 或 lopc_fh，None 不额外筛选模型
OUTPUT_PATH = Path("work/visualization/output/position.png")


def parameter_image(rows, parameter_name, peak_id, model_name=None):
    """把指定峰的已有参数摆放到网格，重复记录报错，不计算统计量。"""
    if not rows or parameter_name not in rows[0]:
        raise ValueError("参数表为空，或找不到指定参数列")
    points = {}
    for row in rows:
        if int(float(row["peak_id"])) != peak_id:
            continue
        if model_name is not None and row.get("model", "").strip().lower() != model_name.lower():
            continue
        key = (int(float(row["y"])), int(float(row["x"])))
        if key in points:
            raise ValueError(f"空间点 {key} 的所选峰有重复记录，请先明确选择")
        points[key] = float(row[parameter_name])
    if not points:
        raise ValueError("没有符合 PEAK_ID 和 MODEL_NAME 的记录")
    image = np.full((max(y for y, _ in points) + 1, max(x for _, x in points) + 1), np.nan)
    for (y, x), value in points.items():
        image[y, x] = value
    return image


def main():
    with PARAMETERS_PATH.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    image = parameter_image(rows, PARAMETER_NAME, PEAK_ID, MODEL_NAME)
    figure, axis = plt.subplots(figsize=(6, 5))
    image_plot = axis.imshow(image, origin="lower", aspect="auto")
    figure.colorbar(image_plot, ax=axis, label=PARAMETER_NAME)
    axis.set(xlabel="x", ylabel="y", title=f"{PARAMETER_NAME}, peak_id={PEAK_ID}")
    figure.tight_layout()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT_PATH, dpi=150)
    plt.close(figure)
    print(f"已保存图片：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
