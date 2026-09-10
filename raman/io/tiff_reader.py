"""TIFF 拉曼光谱立方体的读取方法。"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from raman.data import RamanData


def read_tiff(
    path: str | Path,
    *,
    raman_shift_start: float = 350.0,
    raman_shift_end: float = 800.0,
    **_: object,
) -> RamanData:
    """读取三维 TIFF，并统一为 ``(y, x, 拉曼位移)`` 顺序。"""
    try:
        import tifffile
    except ImportError as exc:
        raise RuntimeError("TIFF input requires tifffile.") from exc

    input_path = Path(path)
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    array = np.asarray(tifffile.imread(input_path))
    if array.ndim != 3:
        raise ValueError(f"Expected a 3-D TIFF spectral cube, got shape {array.shape}")

    spectral_dimension = int(np.argmax(array.shape))
    cube = np.moveaxis(array.astype(float), spectral_dimension, -1)
    y_size, x_size, shift_size = cube.shape
    shifts = np.linspace(raman_shift_start, raman_shift_end, shift_size)
    return RamanData(
        "cube",
        np.arange(x_size, dtype=float),
        cube,
        np.arange(y_size, dtype=float),
        shifts,
    )
