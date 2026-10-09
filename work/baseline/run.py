"""估计 TIFF 光谱立方体中选定空间点的背景。

可以修改下面的常量重复执行分析，也可以通过命令行参数覆盖输入、输出和
空间范围。输出为 ``output/background.tif``、``output/corrected.tif`` 及元数据。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.baseline import airpls
from raman.io import read_tiff

READ_DATA = read_tiff
BASELINE_METHOD = airpls
INPUT_PATH = Path("input.tif")
OUTPUT_DIR = Path(__file__).parent / "output"
READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}
BASELINE_OPTIONS = {"lam": 1e6, "diff_order": 2, "max_iter": 50}
Y_START, Y_END = 0, None
X_START, X_END = 0, None


def process_cube(
    input_path: str | Path = INPUT_PATH,
    output_dir: str | Path = OUTPUT_DIR,
    *,
    y_start: int = Y_START,
    y_end: int | None = Y_END,
    x_start: int = X_START,
    x_end: int | None = X_END,
) -> tuple[np.ndarray, dict]:
    data = READ_DATA(input_path, **READER_OPTIONS)
    if data.kind != "cube" or data.spectral_axis is None or data.y is None:
        raise ValueError("基线工作流需要三维 TIFF 光谱立方体")
    cube = np.asarray(data.intensity, dtype=float)
    y_stop = cube.shape[0] if y_end is None else min(y_end, cube.shape[0])
    x_stop = cube.shape[1] if x_end is None else min(x_end, cube.shape[1])
    if not (0 <= y_start <= y_stop and 0 <= x_start <= x_stop):
        raise ValueError("Processing range is outside the input cube")
    background = np.full_like(cube, np.nan, dtype=float)
    for y_index in range(y_start, y_stop):
        for x_index in range(x_start, x_stop):
            signal = cube[y_index, x_index]
            finite = np.isfinite(signal)
            if not finite.any():
                continue
            working = signal if finite.all() else np.interp(
                data.spectral_axis,
                data.spectral_axis[finite],
                signal[finite],
            )
            _, baseline = BASELINE_METHOD(
                data.spectral_axis, working, **BASELINE_OPTIONS
            )
            background[y_index, x_index] = baseline

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    try:
        import tifffile
    except ImportError as exc:
        raise RuntimeError("写入 TIFF 输出需要 tifffile") from exc
    tifffile.imwrite(directory / "background.tif", background.astype(np.float32))
    tifffile.imwrite(directory / "corrected.tif", (cube - background).astype(np.float32))
    metadata = {
        "dimension_order": ["y", "x", "raman_shift"],
        "shape": list(background.shape),
        "raman_shift_range": [float(data.spectral_axis[0]), float(data.spectral_axis[-1])],
        "dtype": "float32",
        "processing_range": {"y": [y_start, y_stop], "x": [x_start, x_stop]},
        "baseline_method": getattr(BASELINE_METHOD, "__name__", str(BASELINE_METHOD)),
        "baseline_options": BASELINE_OPTIONS,
        "input_file": str(Path(input_path)),
    }
    (directory / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return background, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--y-start", type=int, default=Y_START)
    parser.add_argument("--y-end", type=int, default=Y_END)
    parser.add_argument("--x-start", type=int, default=X_START)
    parser.add_argument("--x-end", type=int, default=X_END)
    args = parser.parse_args()
    _, metadata = process_cube(
        args.input,
        args.output,
        y_start=args.y_start,
        y_end=args.y_end,
        x_start=args.x_start,
        x_end=args.x_end,
    )
    print(f"Wrote {Path(args.output) / 'background.tif'}")
    print(f"Wrote {Path(args.output) / 'corrected.tif'}")
    print(f"Processed y={metadata['processing_range']['y']}, x={metadata['processing_range']['x']}")


if __name__ == "__main__":
    main()
