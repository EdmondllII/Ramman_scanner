"""将多个两列 CSV 光谱绘制在同一坐标轴中。"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from raman.io import read_csv_spectrum
except ImportError:  # 直接运行此文件时补充项目根目录。
    import sys
    sys.path.insert(0, str(Path(__file__).parents[2]))
    from raman.io import read_csv_spectrum


def plot_comparison(paths: list[str | Path], output: str | Path) -> None:
    import matplotlib.pyplot as plt
    figure, axis = plt.subplots(figsize=(8, 4.5))
    for path in paths:
        x, y = read_csv_spectrum(path)
        axis.plot(x, y, label=Path(path).stem)
    axis.set(xlabel="Raman shift", ylabel="Intensity"); axis.legend(); figure.tight_layout(); figure.savefig(output, dpi=150); plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("paths", nargs="+", type=Path); parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); args.output.parent.mkdir(parents=True, exist_ok=True); plot_comparison(args.paths, args.output)


if __name__ == "__main__":
    main()
