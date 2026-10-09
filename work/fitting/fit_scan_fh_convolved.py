"""Gaussian 仪器卷积完整 A 项实验：735 cm⁻¹ 附近使用卷积 LOPC × Faust–Henry，其他峰使用 Lorentzian。"""

from pathlib import Path
import csv
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.fitting.lopc_fh_convolved import fit as lopc
from raman.fitting import detect_peaks, lorentzian  # 三个名称分别指向寻峰、LOPC.fit 和 Lorentzian.fit
from raman.io import read_csv_spectrum, read_tiff  # 支持校正 TIFF 或单条校正 CSV
from raman.fitting.weighting import saturation_weights

INPUT_PATH = Path("work/baseline/output/corrected.tif")  # 已扣除背景的 TIFF 或单条 CSV
OUTPUT_PATH = Path("work/fitting/output/fit_parameters_lopc_fh_convolved.csv")  # LOPC 混合拟合参数 CSV
READER_OPTIONS = {"raman_shift_start": 350.0, "raman_shift_end": 800.0}  # Raman 位移范围
FIT_OPTIONS = {"sigma": None, "vary_centers": True}  # Lorentzian 参数
# enabled=False 恢复普通最小二乘，此时 alpha、scale 不生效。
WEIGHT_OPTIONS = {"enabled": True, "alpha": 6.0, "scale": 3}  # scale 为强度单位；平方误差权重范围 1 至 1+alpha
LOPC_RANGE = (720.0, 750.0)  # 735 cm^-1 附近的 LOPC 候选范围
LOPC_OPTIONS = {  # LOPC 初值、材料参数和仪器响应
    "C": 0.0,  # 有符号、无量纲的初值；不采用文献的固定数值
    "vary_C": True,  # True 时 Adam 和 LM 均拟合 C，不设人为上下限
    "omega_t": 533.0,
    "epsilon_inf": 9.5,
    "omega_p": 220.0,
    "gamma_p": 80.0,
    "gamma_ph": 7.0,
    "optimizer": "lm",  # 卷积模型直接使用 LM，Adam 预优化尚未接入卷积目标函数
    "adam_options": {  # Adam 只作为 LOPC 的初值搜索阶段
        "learning_rate": 0.02,
        "max_steps": 1000,
        "patience": 150,
        "seed": 0,
    },
    "sigma_inst": 1.0,  # Gaussian 仪器响应的标准差，单位 cm^-1；先使用固定标定候选值
}
Y_START, Y_END = 0, 1  # y 范围；改为 3, 4 就只处理 y=3
X_START, X_END = 0, 1  # x 范围；改为 5, 6 就只处理 x=5

is_csv = INPUT_PATH.suffix.lower() == ".csv"
if is_csv:
    csv_shifts, csv_spectrum = read_csv_spectrum(INPUT_PATH)
    data = None
    cube = None
else:
    data = read_tiff(INPUT_PATH, **READER_OPTIONS)
    if data.kind != "cube" or data.spectral_axis is None:
        raise ValueError("TIFF 输入必须是三维校正光谱立方体")
    cube = np.asarray(data.intensity, dtype=float)
    csv_shifts = csv_spectrum = None

shift_axis = csv_shifts if is_csv else data.spectral_axis
SAMPLING_STEP_CM = (shift_axis[-1] - shift_axis[0]) / (shift_axis.size - 1)  # cm⁻¹/点，由已有位移轴获取
PEAK_OPTIONS = {"prominence": None, "distance": 3}  # distance 单位 cm⁻¹

records = []
y_end = 1 if is_csv else (cube.shape[0] if Y_END is None else min(Y_END, cube.shape[0]))
x_end = 1 if is_csv else (cube.shape[1] if X_END is None else min(X_END, cube.shape[1]))

for y in range(Y_START, y_end):  # 修改这里的范围即可选择空间点
    for x in range(X_START, x_end):  # 修改这里的范围即可选择空间点
        corrected = csv_spectrum if is_csv else cube[y, x]  # 输入已经是基线校正后的光谱
        shifts_source = csv_shifts if is_csv else data.spectral_axis
        finite = np.isfinite(corrected) & np.isfinite(shifts_source)  # 拟合前同时排除无效位移和强度
        if finite.sum() < 3:
            continue
        shifts = shifts_source[finite]  # 当前空间点的有效 Raman 位移
        spectrum = corrected[finite]  # 当前空间点的有效校正强度
        weights = saturation_weights(spectrum, alpha=WEIGHT_OPTIONS["alpha"], scale=WEIGHT_OPTIONS["scale"]) if WEIGHT_OPTIONS["enabled"] else None
        centers = detect_peaks(shifts, spectrum, **{**PEAK_OPTIONS, "distance": max(1, int(np.ceil(PEAK_OPTIONS["distance"] / SAMPLING_STEP_CM)))})  # cm⁻¹ 换回寻峰所需的采样点数
        if centers.size == 0:
            continue

        lopc_indexes = np.flatnonzero(  # 找出落入 720--750 cm^-1 窗口的候选峰序号
            (centers >= LOPC_RANGE[0]) & (centers <= LOPC_RANGE[1])
        )
        lopc_index = None
        if lopc_indexes.size == 1:  # 只有恰好一个候选峰时才启用 LOPC
            lopc_index = int(lopc_indexes[0])  # 保存它在完整 centers 数组中的位置

        lorentz_indexes = [  # 除 LOPC 候选峰外，其余检测峰全部交给 Lorentzian
            index for index in range(centers.size) if index != lopc_index
        ]
        lorentz_result = None
        if lorentz_indexes:
            lorentz_mask = np.ones(shifts.size, dtype=bool)  # 默认让 Lorentzian 使用整条光谱
            if lopc_index is not None:
                lorentz_mask = (  # 已启用 LOPC 时，从 Lorentzian 数据中挖掉对应窗口
                    (shifts < LOPC_RANGE[0]) | (shifts > LOPC_RANGE[1])
                )
            lorentz_result = lorentzian(  # 多个 Lorentzian 分量在一次联合最小二乘中拟合
                shifts[lorentz_mask],
                spectrum[lorentz_mask],
                centers=centers[lorentz_indexes],
                weights=None if weights is None else weights[lorentz_mask],
                **FIT_OPTIONS,
            )

        lopc_result = None
        lopc_shifts = None
        if lopc_index is not None:
            lopc_mask = (  # LOPC 只观察设定窗口内的数据
                (shifts >= LOPC_RANGE[0]) & (shifts <= LOPC_RANGE[1])
            )
            lopc_shifts = shifts[lopc_mask]
            lopc_spectrum = spectrum[lopc_mask]
            if lopc_shifts.size < 3:
                raise ValueError("LOPC 拟合窗口内至少需要三个有效光谱点")
            lopc_result = lopc(  # 用检测峰位作为 omega_l 初值进入 LOPC 非线性拟合
                lopc_shifts,
                lopc_spectrum,
                centers=[centers[lopc_index]],
                weights=None if weights is None else weights[lopc_mask],
                **LOPC_OPTIONS,
            )

        lorentz_position = 0
        for peak_id, center in enumerate(centers, 1):
            if peak_id - 1 == lopc_index:
                fitted = lopc_result.eval(x=lopc_shifts)  # 用最优参数重新计算窗口内的拟合曲线
                height = float(np.max(fitted))
                if height <= 0.0:
                    continue
                peak_position = float(lopc_shifts[np.argmax(fitted)])  # 离散曲线最大值位置，不等同于 omega_l
                records.append({
                    "x": x,
                    "y": y,
                    "peak_id": peak_id,
                    "model": "lopc_fh_convolved",
                    "position": peak_position,
                    "height": height,
                    "amplitude": lopc_result.params["amplitude"].value,
                    "sigma": np.nan,
                    "gamma": np.nan,
                    "fwhm": np.nan,
                    "omega_l": lopc_result.params["omega_l"].value,
                    "omega_p": lopc_result.params["omega_p"].value,
                    "gamma_p": lopc_result.params["gamma_p"].value,
                    "gamma_ph": lopc_result.params["gamma_ph"].value,
                    "omega_t": lopc_result.params["omega_t"].value,
                    "epsilon_inf": lopc_result.params["epsilon_inf"].value,
                    "C": lopc_result.params["C"].value,
                    "sigma_inst": lopc_result.params["sigma_inst"].value,
                })
                continue

            prefix = f"p{lorentz_position + 1}_"  # 与 lorentzian.fit 中的分量参数前缀保持一致
            lorentz_position += 1
            height = float(lorentz_result.params[f"{prefix}height"].value)
            if height <= 0.0:
                continue
            records.append({
                "x": x,
                "y": y,
                "peak_id": peak_id,
                "model": "lorentzian",
                "position": lorentz_result.params[f"{prefix}center"].value,
                "height": height,
                "amplitude": lorentz_result.params[f"{prefix}amplitude"].value,
                "sigma": lorentz_result.params[f"{prefix}sigma"].value,
                "gamma": np.nan,
                "fwhm": lorentz_result.params[f"{prefix}fwhm"].value,
                "omega_l": np.nan,
                "omega_p": np.nan,
                "gamma_p": np.nan,
                "gamma_ph": np.nan,
                "omega_t": np.nan,
                "epsilon_inf": np.nan,
                "C": np.nan,
                "sigma_inst": np.nan,
            })

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
fields = [
    "x", "y", "peak_id", "model",
    "position", "height", "amplitude", "sigma", "gamma", "fwhm",
    "omega_l", "omega_p", "gamma_p", "gamma_ph", "omega_t", "epsilon_inf", "C", "sigma_inst",
]
with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)
print(f"已保存拟合参数：{OUTPUT_PATH}")
