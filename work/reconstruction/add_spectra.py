"""将两个两列 CSV 光谱相加。"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.io import read_csv_spectrum


def combine(first: str | Path, second: str | Path, output: str | Path, sign: float = 1.0) -> None:
    """在第一个光谱坐标轴上执行两个光谱的加法。"""
    x1, y1 = read_csv_spectrum(first)
    x2, y2 = read_csv_spectrum(second)
    if np.array_equal(x1, x2):
        result = y1 + sign * y2
    else:
        result = y1 + sign * np.interp(x1, x2, y2)
    np.savetxt(output, np.column_stack((x1, result)), delimiter=",", header="raman_shift,intensity", comments="")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path); parser.add_argument("second", type=Path); parser.add_argument("output", type=Path)
    args = parser.parse_args(); combine(args.first, args.second, args.output)


if __name__ == "__main__":
    main()
