# 可视化

本目录只读取已有数据和结果并绘图，不拟合、不重建、不扣背景、不计算拟合评估指标。拟合曲线对比使用 `plot_spectra_comparison.py`；原始、背景和校正谱对比使用 `plot_single_spectrum.py`；参数空间分布使用 `plot_parameter_heatmap.py`。所有命令在项目根目录执行，图片默认保存到 `output/`。

## plot_spectra_comparison.py

```bash
python work/visualization/plot_spectra_comparison.py
```

**用途与方法**：在同一张图中对比多条光谱，第一条画黑色散点，其余画红色细线。

**输入、输出**：`INPUT_PATHS` 中的两列 CSV，默认读取 `work/baseline/output/corrected_x0_y0.csv`（由 `baseline_scan.py` 生成）和 `work/reconstruction/output/reconstructed.csv`（由 `reconstruct_spectrum.py` 生成）。`OUTPUT_PATH` 默认 `work/visualization/output/comparison.png`。

**需要修改的配置**：顶部 `INPUT_PATHS`、`OUTPUT_PATH`；各输入应对应同一空间点和可比较的位移范围。

## plot_spectra_comparison_fh.py

```bash
python work/visualization/plot_spectra_comparison_fh.py
```

**用途与方法**：绘制校正谱和完整 A 项的独立重建谱；先运行新拟合和新重建。

**输入、输出**：读取 `corrected_x0_y0.csv` 和 `work/reconstruction/output/reconstructed_fh.csv`；输出 `work/visualization/output/comparison_fh.png`。

**需要修改的配置**：顶部 `INPUT_PATHS`、`OUTPUT_PATH`。输入应对应同一空间点；可以额外加入旧 `reconstructed.csv` 对照。

## plot_spectra_comparison_fh_convolved.py

```bash
python work/visualization/plot_spectra_comparison_fh_convolved.py
```

**用途与方法**：绘制校正谱和 Gaussian 仪器卷积完整 A 项重建谱；只读取已有 CSV，不计算卷积。

**输入、输出**：读取 `corrected_x0_y0.csv` 和 `work/reconstruction/output/reconstructed_fh_convolved.csv`；输出 `work/visualization/output/comparison_fh_convolved.png`。

**需要修改的配置**：顶部 `INPUT_PATHS`、`OUTPUT_PATH`。

## plot_single_spectrum.py

```bash
python work/visualization/plot_single_spectrum.py
```

**用途与方法**：绘制指定点的原始、背景和校正谱，三条曲线均读取已有文件；校正谱由 baseline 步骤生成。

**输入、输出**：`RAW_PATH` 默认 `input.tif`，`BACKGROUND_PATH` 默认 `work/baseline/output/background.tif`，`CORRECTED_PATH` 默认 `work/baseline/output/corrected.tif`；`OUTPUT_PATH` 默认 `work/visualization/output/spectrum.png`。

**需要修改的配置**：顶部三个输入路径、输出路径、`X/Y`（默认 0、0）、`READER_OPTIONS`。三份输入应对应同一数据和点位，位移范围应与基线设置一致。

## plot_parameter_heatmap.py

```bash
python work/visualization/plot_parameter_heatmap.py
```

**用途与方法**：绘制指定峰的已有参数，不对不同峰取平均。通过 `PEAK_ID` 和可选 `MODEL_NAME` 筛选；同一空间点存在重复匹配时报错。

**输入、输出**：`PARAMETERS_PATH` 默认 `work/fitting/output/fit_parameters.csv`；`OUTPUT_PATH` 默认 `work/visualization/output/position.png`。

**需要修改的配置**：顶部 `PARAMETERS_PATH`、`PARAMETER_NAME`（默认 `position`）、`PEAK_ID`（默认 1）、`MODEL_NAME`（默认 None）、`OUTPUT_PATH`。缺失值保持 NaN，不插值或平均。峰编号由各点寻峰顺序产生，并不自动保证不同空间点的同编号属于同一物理模式，绘图前需确认选峰。
