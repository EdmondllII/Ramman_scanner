"""根据逐点拟合参数表重建一条谱线。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Callable

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.io import read_csv_spectrum, read_tiff
from raman.reconstruction import reconstruct_gaussian

PARAMETERS_PATH = Path(__file__).parents[1] / "fitting" / "output" / "fit_parameters.csv"
OUTPUT_DIR = Path(__file__).parent / "output"
SHIFT_SOURCE_PATH = Path("input.tif")
READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}
RECONSTRUCT_METHOD = reconstruct_gaussian
# 值可以是列名（推荐），也可以是无表头文件中的从零开始的列序号。
PARAMETER_MAPPING: dict[str, object] = {
    "x": "x", "y": "y", "peak_id": "peak_id",
    "center": "position", "amplitude": "amplitude", "sigma": "sigma",
}


def read_shift_axis(path: str | Path) -> np.ndarray:
    """从原始 TIFF 或两列 CSV 光谱中读取 Raman 位移坐标。"""
    source = Path(path)
    if source.suffix.lower() in {".tif", ".tiff"}:
        data = read_tiff(source, **READER_OPTIONS)
        if data.spectral_axis is None:
            raise ValueError(f"无法从文件读取 Raman 位移轴：{source}")
        return data.spectral_axis.copy()
    shifts, _ = read_csv_spectrum(source)
    return shifts


def _read_rows(path: Path) -> tuple[list[str] | None, list[list[str]]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.reader(stream))
    if not rows:
        raise ValueError(f"No rows found in {path}")
    try:
        [float(value) for value in rows[0]]
    except ValueError:
        return rows[0], rows[1:]
    return None, rows


def _value(row: list[str], header: list[str] | None, spec: object) -> float:
    conversion = None
    if isinstance(spec, dict):
        conversion = spec.get("conversion")
        spec = spec.get("column")
    index = header.index(str(spec)) if header is not None and isinstance(spec, str) else int(spec)
    result = float(row[index])
    if conversion == "fwhm_to_sigma":
        result /= 2.0 * np.sqrt(2.0 * np.log(2.0))
    return result


def reconstruct_spectrum(
    parameters_path: str | Path = PARAMETERS_PATH,
    *,
    x_coordinate: float,
    y_coordinate: float,
    shifts: np.ndarray,
    peak_ids: set[int] | None = None,
    parameter_mapping: dict[str, object] | None = None,
    method: Callable[..., np.ndarray] = RECONSTRUCT_METHOD,
) -> tuple[np.ndarray, list[dict[str, float]]]:
    header, rows = _read_rows(Path(parameters_path))
    mapping = parameter_mapping or PARAMETER_MAPPING
    selected: list[dict[str, float]] = []
    total = np.zeros_like(shifts, dtype=float)
    for row in rows:
        if not row or len(row) < 1:
            continue
        values = {name: _value(row, header, mapping[name]) for name in ("x", "y", "peak_id")}
        if not (np.isclose(values["x"], x_coordinate) and np.isclose(values["y"], y_coordinate)):
            continue
        if peak_ids is not None and int(values["peak_id"]) not in peak_ids:
            continue
        values.update({name: _value(row, header, mapping[name]) for name in ("center", "amplitude", "sigma")})
        total += method(
            shifts,
            center=values["center"],
            amplitude=values["amplitude"],
            sigma=values["sigma"],
        )
        selected.append(values)
    return total, selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameters", type=Path, default=PARAMETERS_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--x", type=float, required=True)
    parser.add_argument("--y", type=float, required=True)
    parser.add_argument("--peak-id", type=int, action="append", dest="peak_ids")
    parser.add_argument(
        "--shift-source",
        type=Path,
        default=SHIFT_SOURCE_PATH,
        help="原始 TIFF 或两列 CSV 光谱，用于提供 Raman 位移坐标",
    )
    args = parser.parse_args()
    shifts = read_shift_axis(args.shift_source)
    spectrum, selected = reconstruct_spectrum(
        args.parameters, x_coordinate=args.x, y_coordinate=args.y,
        shifts=shifts, peak_ids=set(args.peak_ids) if args.peak_ids else None,
    )
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"spectrum_x{args.x:g}_y{args.y:g}.csv"
    np.savetxt(output_path, np.column_stack((shifts, spectrum)), delimiter=",", header="raman_shift,intensity", comments="")
    (output_dir / "metadata.json").write_text(json.dumps({
        "input_parameters": str(args.parameters), "x": args.x, "y": args.y,
        "peak_ids": args.peak_ids, "method": getattr(RECONSTRUCT_METHOD, "__name__", str(RECONSTRUCT_METHOD)),
        "shift_source": str(args.shift_source), "output": str(output_path),
        "points": int(shifts.size), "peak_count": len(selected),
    }, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
