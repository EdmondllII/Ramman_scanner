# 光谱重建与运算

当前 LOPC 混合模型使用 `reconstruct_spectrum.py`；原有参数表使用 `reconstruct_from_parameters.py`。加减脚本处理已有 CSV 光谱。所有命令在项目根目录执行。

## reconstruct_spectrum.py

```bash
python work/reconstruction/reconstruct_spectrum.py
```

**用途与模型**：重建指定点的全部或选定峰。当前混合表按 `model` 列的 `lorentzian`、`lopc` 分派对应函数；没有模型标记的表使用 `RECONSTRUCT_METHOD`，默认 Gaussian。

**输入、输出**：`PARAMETERS_PATH` 默认 `work/fitting/output/fit_parameters_lopc.csv`；`SHIFT_SOURCE_PATH` 默认 `work/baseline/output/corrected.tif`，只提供位移轴，也支持两列 CSV；`OUTPUT_PATH` 默认 `work/reconstruction/output/reconstructed.csv`，为两列总重建谱。

**需要修改的配置**：顶部路径、`X_COORDINATE/Y_COORDINATE`（默认 0、0）、`PEAK_IDS`（默认全部峰）、`PARAMETER_MAPPING`（列名映射）、`READER_OPTIONS` 和旧表使用的 `RECONSTRUCT_METHOD`。重建方法应与拟合方法一致。

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

**用途与方法**：两条光谱相加；位移轴不同时，将第二条插值到第一条的轴上。

**输入、输出**：两列 CSV，默认输入 `first.csv`、`second.csv`，默认输出 `work/reconstruction/output/sum.csv`。

**需要修改的配置**：顶部 `FIRST_PATH`、`SECOND_PATH`、`OUTPUT_PATH`；检查两条输入的位移覆盖范围。

## subtract_spectra.py

```bash
python work/reconstruction/subtract_spectra.py
```

**用途与方法**：第一条光谱减去第二条；位移轴不同时，将第二条插值到第一条的轴上。

**输入、输出**：两列 CSV，默认输入 `first.csv`、`background.csv`，默认输出 `work/reconstruction/output/difference.csv`。

**需要修改的配置**：顶部 `FIRST_PATH`、`SECOND_PATH`、`OUTPUT_PATH`；第一条为被减光谱，第二条为扣除项，并检查位移覆盖范围。
