"""拉曼数据处理入口：读取数据、基线矫正并进行峰拟合。"""

from pathlib import Path

import numpy as np

from raman.baseline import airpls
from raman.fitting import detect_peaks, gaussian, spectrum_data
from raman.io import read_tiff
from raman.output import save_cube_results, save_fit_result


# 从 raman.io、raman.baseline 和 raman.fitting 导入并选择要使用的方法。
# 更换下面的方法名称及对应参数字典即可改变处理方案。
READ_DATA = read_tiff
BASELINE_METHOD = airpls
FIT_METHOD = gaussian

INPUT_PATH = Path(r"E:\Edmon\datas\chipdatas\B144XA04001-230515-NC2176\-26_132.tif")
OUTPUT_DIR = Path("raman_output")

READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}
BASELINE_OPTIONS = {"lam": 1e6, "diff_order": 2, "max_iter": 50}
PEAK_OPTIONS = {"prominence": None, "distance": 3}
FIT_OPTIONS = {"sigma": None, "vary_centers": True}


def main() -> None:
    data = READ_DATA(INPUT_PATH, **READER_OPTIONS)

    if data.kind == "cube":
        _process_cube(data)
        print(f"Read {INPUT_PATH}")
        print(f"Processed every spatial point: {data.intensity.shape[:2]}")
        print(f"Wrote results to {OUTPUT_DIR.resolve()}")
        return

    x, raw_signal = spectrum_data(data)
    corrected_signal, baseline = BASELINE_METHOD(x, raw_signal, **BASELINE_OPTIONS)
    peak_centers = detect_peaks(x, corrected_signal, **PEAK_OPTIONS)
    fit_result = FIT_METHOD(x, corrected_signal, centers=peak_centers, **FIT_OPTIONS)
    save_fit_result(
        OUTPUT_DIR,
        x,
        raw_signal,
        baseline,
        corrected_signal,
        fit_result,
    )
    print(f"Read {INPUT_PATH}")
    print(f"Detected {peak_centers.size} peaks")
    print(f"Wrote results to {OUTPUT_DIR.resolve()}")


def _process_cube(data) -> None:
    """逐个处理每个 ``(y, x)`` 空间点的光谱，并保存空间结果。"""
    if data.spectral_axis is None or data.y is None:
        raise ValueError("A spectral cube must provide spatial and Raman-shift axes")

    cube = data.intensity
    baseline_cube = np.empty_like(cube, dtype=float)
    corrected_cube = np.empty_like(cube, dtype=float)
    fitted_cube = np.full_like(cube, np.nan, dtype=float)
    records: list[dict[str, float]] = []

    for y_index in range(1):#cube.shape[0]):
        for x_index in range(1):#cube.shape[1]):
            signal = np.asarray(cube[y_index, x_index], dtype=float)
            finite = np.isfinite(signal)
            if not finite.any():
                baseline_cube[y_index, x_index] = np.nan
                corrected_cube[y_index, x_index] = np.nan
                continue
            if not finite.all():
                signal = signal.copy()
                signal[~finite] = np.interp(
                    data.spectral_axis[~finite],
                    data.spectral_axis[finite],
                    signal[finite],
                )
            corrected, baseline = BASELINE_METHOD(
                data.spectral_axis, signal, **BASELINE_OPTIONS
            )
            baseline_cube[y_index, x_index] = baseline
            corrected_cube[y_index, x_index] = corrected
            centers = detect_peaks(data.spectral_axis, corrected, **PEAK_OPTIONS)
            if centers.size == 0:
                continue
            result = FIT_METHOD(
                data.spectral_axis, corrected, centers=centers, **FIT_OPTIONS
            )
            fitted_cube[y_index, x_index] = result.best_fit
            for peak_id, center in enumerate(centers, 1):
                prefix = f"p{peak_id}_"
                records.append(
                    {
                        "y_index": float(y_index),
                        "x_index": float(x_index),
                        "peak_id": float(peak_id),
                        "position": float(result.params[f"{prefix}center"].value),
                        "height": float(result.params[f"{prefix}height"].value),
                        "amplitude": float(result.params[f"{prefix}amplitude"].value),
                        "sigma": float(result.params[f"{prefix}sigma"].value),
                        "fwhm": float(result.params[f"{prefix}fwhm"].value),
                    }
                )

    save_cube_results(
        OUTPUT_DIR,
        data,
        baseline_cube,
        corrected_cube,
        fitted_cube,
        records,
    )


if __name__ == "__main__":
    main()
