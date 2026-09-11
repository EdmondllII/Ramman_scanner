"""将指定的逐点拟合参数绘制为空间热力图。"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


def plot_heatmap(parameters_path: str | Path, parameter: str, output: str | Path) -> None:
    import matplotlib.pyplot as plt
    with Path(parameters_path).open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("Fit parameter file contains no records")
    if parameter not in rows[0]:
        raise ValueError(f"Unknown parameter {parameter!r}; available columns: {', '.join(rows[0])}")
    points: dict[tuple[int, int], list[float]] = {}
    for row in rows:
        key = (int(float(row["y"])), int(float(row["x"])))
        points.setdefault(key, []).append(float(row[parameter]))
    y_max = max(y for y, _ in points); x_max = max(x for _, x in points)
    image = np.full((y_max + 1, x_max + 1), np.nan)
    for (y, x), values in points.items():
        image[y, x] = float(np.mean(values))
    figure, axis = plt.subplots(figsize=(6, 5)); image_plot = axis.imshow(image, origin="lower", aspect="auto"); figure.colorbar(image_plot, ax=axis, label=parameter)
    axis.set(xlabel="x", ylabel="y", title=parameter); figure.tight_layout(); figure.savefig(output, dpi=150); plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("parameters", type=Path); parser.add_argument("parameter"); parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); args.output.parent.mkdir(parents=True, exist_ok=True); plot_heatmap(args.parameters, args.parameter, args.output)


if __name__ == "__main__":
    main()
