# 可视化

本目录只读取已有数据和结果。拟合曲线对比使用 `plot_spectra_comparison.py`；原始、背景和校正谱对比使用 `plot_single_spectrum.py`；参数空间分布使用 `plot_parameter_heatmap.py`。所有命令在项目根目录执行，图片默认保存到 `output/`。

## plot_spectra_comparison.py

```bash
python work/visualization/plot_spectra_comparison.py
```

**用途与方法**：在同一张图中对比多条光谱，第一条画黑色散点，其余画红色细线。

**输入、输出**：`INPUT_PATHS` 中的两列 CSV，默认读取 `work/visualization/output/corrected_x0_y0.csv`（由 `baseline_scan.py` 生成）和 `work/reconstruction/output/reconstructed.csv`（由 `reconstruct_spectrum.py` 生成）。`OUTPUT_PATH` 默认 `work/visualization/output/comparison.png`。

**需要修改的配置**：顶部 `INPUT_PATHS`、`OUTPUT_PATH`；各输入应对应同一空间点和可比较的位移范围。

## plot_single_spectrum.py

```bash
python work/visualization/plot_single_spectrum.py
```

**用途与方法**：绘制指定点的原始、背景和校正谱，校正谱通过原始谱减背景计算。

**输入、输出**：`RAW_PATH` 默认 `input.tif`，`BACKGROUND_PATH` 默认 `work/baseline/output/background.tif`；`OUTPUT_PATH` 默认 `work/visualization/output/spectrum.png`。

**需要修改的配置**：顶部路径、`X/Y`（默认 0、0）、`READER_OPTIONS`。原始数据与背景应对应同一数据和点位，位移范围应与基线设置一致。

## plot_parameter_heatmap.py

```bash
python work/visualization/plot_parameter_heatmap.py
```

**用途与方法**：将指定参数列绘制为空间热力图。同一点有多个峰时，当前实现取该列所有峰的平均值，不单独筛选某个峰。

**输入、输出**：`PARAMETERS_PATH` 默认 `work/fitting/output/fit_parameters.csv`；`OUTPUT_PATH` 默认 `work/visualization/output/position.png`。

**需要修改的配置**：顶部 `PARAMETERS_PATH`、`PARAMETER_NAME`（默认 `position`）、`OUTPUT_PATH`。混合表中部分列可能有 `NaN`，且同点平均值不等同于某一物理峰的参数。
