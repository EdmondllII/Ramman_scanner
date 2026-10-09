# 光谱重建与运算

当前 LOPC 混合模型使用 `reconstruct_spectrum.py`；原有参数表使用 `reconstruct_from_parameters.py`。加减脚本处理已有 CSV 光谱。所有命令在项目根目录执行。

## reconstruct_spectrum.py

```bash
python work/reconstruction/reconstruct_spectrum.py
```

**用途与模型**：重建指定点的全部或选定峰。当前混合表按 `model` 列的 `lorentzian`、`lopc` 分派对应函数；没有模型标记的表使用 `RECONSTRUCT_METHOD`，默认 Gaussian。

**输入、输出**：`PARAMETERS_PATH` 默认 `work/fitting/output/fit_parameters_lopc.csv`；`SHIFT_SOURCE_PATH` 默认 `work/baseline/output/corrected.tif`，只提供位移轴，也支持两列 CSV；`OUTPUT_PATH` 默认 `work/reconstruction/output/reconstructed.csv`，为两列总重建谱。

**需要修改的配置**：顶部路径、`X_COORDINATE/Y_COORDINATE`（默认 0、0）、`PEAK_IDS`（默认全部峰）、`PARAMETER_MAPPING`（列名映射）、`READER_OPTIONS` 和旧表使用的 `RECONSTRUCT_METHOD`。重建方法应与拟合方法一致。

## reconstruct_spectrum_fh.py

```bash
python work/reconstruction/reconstruct_spectrum_fh.py
```

**用途与模型**：独立完整 A 项重建。`lopc_fh` 行使用拟合得到的 C 和 `A_FH * Im[-1/ε]`，Lorentzian 行按原线型重建；其他模型标记会报错，避免误用旧 LOPC 表。

**输入、输出**：读取 `work/fitting/output/fit_parameters_lopc_fh.csv`，共用校正谱的位移轴；输出 `work/reconstruction/output/reconstructed_fh.csv`。

**需要修改的配置**：顶部路径、坐标、`PEAK_IDS`、位移轴读取配置与列名映射。C 必须来自新参数表，不能替换成初值或文献数值。

## reconstruct_spectrum_fh_convolved.py

```bash
python work/reconstruction/reconstruct_spectrum_fh_convolved.py
```

**用途与模型**：独立重建 Gaussian 仪器卷积完整 A 项。`lopc_fh_convolved` 行使用参数表中的 C 和固定 `sigma_inst`，Lorentzian 行保持原线型。

**输入、输出**：读取 `work/fitting/output/fit_parameters_lopc_fh_convolved.csv` 和校正 TIFF 的位移轴；输出 `work/reconstruction/output/reconstructed_fh_convolved.csv`。

**需要修改的配置**：顶部路径、坐标、`PEAK_IDS`、位移轴读取配置和列映射。脚本只使用参数表中的 `sigma_inst`，不重新拟合仪器宽度。

## reconstruct_from_parameters.py

```bash
python work/reconstruction/reconstruct_from_parameters.py --x 0 --y 0
```

**用途与模型**：原有参数表的单点重建，默认 Gaussian，不按 `model` 列自动分派 LOPC。

**输入、输出**：默认读取 `work/fitting/output/fit_parameters.csv`，从 `SHIFT_SOURCE_PATH`（默认 `input.tif`）读取位移轴；在 `OUTPUT_DIR` 保存 `spectrum_x0_y0.csv`、`metadata.json`。

**需要修改的配置**：顶部 `RECONSTRUCT_METHOD`、`PARAMETER_MAPPING`、`READER_OPTIONS`。命令行必须提供 `--x`、`--y`；可用 `--parameters`、`--shift-source`、`--output` 覆盖路径，`--peak-id` 可重复提供以选取多个峰。`--output` 指定目录。

## add_spectra.py

```bash
python work/reconstruction/add_spectra.py
```

**用途与方法**：两条已对齐光谱相加；位移轴不一致时报错，不自动插值。

**输入、输出**：两列 CSV，默认输入 `first.csv`、`second.csv`，默认输出 `work/reconstruction/output/sum.csv`。

**需要修改的配置**：顶部 `FIRST_PATH`、`SECOND_PATH`、`OUTPUT_PATH`；检查两条输入的位移覆盖范围。

## subtract_spectra.py

```bash
python work/reconstruction/subtract_spectra.py
```

**用途与方法**：第一条已对齐光谱减去第二条；位移轴不一致时报错，不自动插值。

**输入、输出**：两列 CSV，默认输入 `first.csv`、`background.csv`，默认输出 `work/reconstruction/output/difference.csv`。

**需要修改的配置**：顶部 `FIRST_PATH`、`SECOND_PATH`、`OUTPUT_PATH`；第一条为被减光谱，第二条为扣除项，并检查位移覆盖范围。
