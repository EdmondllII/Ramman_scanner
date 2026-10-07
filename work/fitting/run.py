"""对光谱立方体中选定的空间点分别进行峰检测和拟合。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.fitting import detect_peaks, gaussian
from raman.io import read_tiff

READ_DATA = read_tiff
FIT_METHOD = gaussian
INPUT_PATH = Path("input.tif")
BACKGROUND_PATH = Path(__file__).parents[1] / "baseline" / "output" / "background.tif"
OUTPUT_DIR = Path(__file__).parent / "output"
READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}
PEAK_OPTIONS = {"prominence": None, "distance": 3}
FIT_OPTIONS = {"sigma": None, "vary_centers": True}
Y_START, Y_END = 0, None
X_START, X_END = 0, None

FIELDS = ["x", "y", "peak_id", "position", "height", "amplitude", "sigma", "fwhm"]


def process_cube(
    input_path: str | Path = INPUT_PATH,
    background_path: str | Path = BACKGROUND_PATH,
    output_dir: str | Path = OUTPUT_DIR,
    *,
    y_start: int = Y_START,
    y_end: int | None = Y_END,
    x_start: int = X_START,
    x_end: int | None = X_END,
) -> tuple[list[dict[str, float]], dict]:
    data = READ_DATA(input_path, **READER_OPTIONS)
    if data.kind != "cube" or data.spectral_axis is None or data.y is None:
        raise ValueError("拟合工作流需要三维 TIFF 光谱立方体")
    try:
        import tifffile
    except ImportError as exc:
        raise RuntimeError("读取 TIFF 背景需要 tifffile") from exc
    background = np.asarray(tifffile.imread(background_path), dtype=float)
    cube = np.asarray(data.intensity, dtype=float)
    if background.shape != cube.shape:
        raise ValueError(f"Background shape {background.shape} does not match cube {cube.shape}")
    y_stop = cube.shape[0] if y_end is None else min(y_end, cube.shape[0])
    x_stop = cube.shape[1] if x_end is None else min(x_end, cube.shape[1])
    if not (0 <= y_start <= y_stop and 0 <= x_start <= x_stop):
        raise ValueError("Processing range is outside the input cube")

    records: list[dict[str, float]] = []
    for y_index in range(y_start, y_stop):
        for x_index in range(x_start, x_stop):
            corrected = cube[y_index, x_index] - background[y_index, x_index]
            finite = np.isfinite(corrected) & np.isfinite(data.spectral_axis)
            if finite.sum() < 3:
                continue
            x_values = data.spectral_axis[finite]
            signal = corrected[finite]
            centers = detect_peaks(x_values, signal, **PEAK_OPTIONS)
            if centers.size == 0:
                continue
            try:
                result = FIT_METHOD(x_values, signal, centers=centers, **FIT_OPTIONS)
            except (ValueError, RuntimeError, np.linalg.LinAlgError):
                continue
            for peak_id, _ in enumerate(centers, 1):
                prefix = f"p{peak_id}_"
                params = result.params
                height = float(params[f"{prefix}height"].value)
                if height <= 0.0:
                    continue
                records.append(
                    {
                        "x": float(x_index),
                        "y": float(y_index),
                        "peak_id": float(peak_id),
                        "position": float(params[f"{prefix}center"].value),
                        "height": height,
                        "amplitude": float(params[f"{prefix}amplitude"].value),
                        "sigma": float(params[f"{prefix}sigma"].value),
                        "fwhm": float(params[f"{prefix}fwhm"].value),
                    }
                )

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "fit_parameters.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    metadata = {
        "dimension_order": ["y", "x", "raman_shift"],
        "raman_shift_range": [float(data.spectral_axis[0]), float(data.spectral_axis[-1])],
        "processing_range": {"y": [y_start, y_stop], "x": [x_start, x_stop]},
        "fit_method": getattr(FIT_METHOD, "__name__", str(FIT_METHOD)),
        "peak_options": PEAK_OPTIONS,
        "fit_options": FIT_OPTIONS,
        "input_file": str(Path(input_path)),
        "background_file": str(Path(background_path)),
        "output_fields": FIELDS,
        "record_count": len(records),
    }
    (directory / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return records, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT_PATH)
    parser.add_argument("--background", type=Path, default=BACKGROUND_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--y-start", type=int, default=Y_START)
    parser.add_argument("--y-end", type=int, default=Y_END)
    parser.add_argument("--x-start", type=int, default=X_START)
    parser.add_argument("--x-end", type=int, default=X_END)
    args = parser.parse_args()
    _, metadata = process_cube(
        args.input, args.background, args.output,
        y_start=args.y_start, y_end=args.y_end,
        x_start=args.x_start, x_end=args.x_end,
    )
    print(f"Wrote {Path(args.output) / 'fit_parameters.csv'} ({metadata['record_count']} peaks)")


if __name__ == "__main__":
    main()
