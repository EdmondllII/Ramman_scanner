"""TXT、CSV 及其他数值文本表格的读取方法。"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from raman.data import RamanData


def _parse_table(path: Path) -> np.ndarray:
    """解析由空格、逗号或分号分隔的数值表格。"""
    if not path.is_file():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    rows: list[list[float]] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1
    ):
        line = raw_line.strip()
        if not line or line.startswith(("#", ";", "//")):
            continue
        line = line.replace(",", " ").replace(";", " ")
        try:
            values = [float(item) for item in line.split()]
        except ValueError:
            if rows:
                raise ValueError(f"Non-numeric row at line {line_number}: {raw_line!r}")
            continue
        if values:
            rows.append(values)

    if not rows:
        raise ValueError(f"No numeric data found in {path}")

    widths = {len(row) for row in rows}
    if len(widths) != 1:
        remaining_widths = {len(row) for row in rows[1:]}
        if len(remaining_widths) == 1 and len(rows[0]) + 1 == next(iter(remaining_widths)):
            rows[0] = [float("nan")] + rows[0]
        else:
            raise ValueError(f"Rows have inconsistent column counts: {sorted(widths)}")
    return np.asarray(rows, dtype=float)


def _strictly_monotonic(values: np.ndarray) -> bool:
    finite = values[np.isfinite(values)]
    if finite.size < 2:
        return False
    differences = np.diff(finite)
    return bool(np.all(differences > 0) or np.all(differences < 0))


def read_txt(path: str | Path, **_: object) -> RamanData:
    """读取两列光谱，或首行首列带坐标的扫描矩阵。"""
    table = _parse_table(Path(path))
    if table.ndim != 2 or table.shape[1] < 2:
        raise ValueError(f"Expected at least two columns, got shape {table.shape}")

    if table.shape[1] == 2:
        order = np.argsort(table[:, 0])
        return RamanData("spectrum", table[order, 0], table[order, 1])

    x_axis = table[0, 1:]
    y_axis = table[1:, 0]
    values = table[1:, 1:]
    if _strictly_monotonic(x_axis) and _strictly_monotonic(y_axis):
        return RamanData("map", x_axis, values, y_axis)

    raise ValueError(
        "Input is neither a two-column spectrum nor a matrix with monotonic "
        "first-row/first-column axes."
    )
