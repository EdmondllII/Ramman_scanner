"""绘制一个空间点的原始光谱、背景和校正光谱。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.io import read_tiff


def plot_single(raw_path: str | Path, background_path: str | Path, x: int, y: int, output: str | Path, *, start: float = 350.0, end: float = 800.0) -> None:
    import tifffile
    import matplotlib.pyplot as plt
    data = read_tiff(raw_path, raman_shift_start=start, raman_shift_end=end)
    background = np.asarray(tifffile.imread(background_path), float)
    raw = np.asarray(data.intensity[y, x], float)
    baseline = background[y, x]
    corrected = raw - baseline
    figure, axis = plt.subplots(figsize=(8, 4.5))
    axis.plot(data.spectral_axis, raw, label="raw")
    axis.plot(data.spectral_axis, baseline, label="background")
    axis.plot(data.spectral_axis, corrected, label="corrected")
    axis.set(xlabel="Raman shift", ylabel="Intensity", title=f"Spectrum at x={x}, y={y}")
    axis.legend(); figure.tight_layout(); figure.savefig(output, dpi=150); plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True); parser.add_argument("--background", type=Path, required=True)
    parser.add_argument("--x", type=int, required=True); parser.add_argument("--y", type=int, required=True); parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); args.output.parent.mkdir(parents=True, exist_ok=True); plot_single(args.raw, args.background, args.x, args.y, args.output)


if __name__ == "__main__":
    main()
