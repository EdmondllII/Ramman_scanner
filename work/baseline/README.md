# 基线估计与矫正

本目录逐空间点估计背景。当前 LOPC 工作流使用 `baseline_scan.py`；`run.py` 是原有背景估计流程。所有命令在项目根目录执行。

## baseline_scan.py

```bash
python work/baseline/baseline_scan.py
```

**用途与方法**：对原始三维 TIFF 的指定空间范围估计背景并扣除。当前 `BASELINE_METHOD` 为 AsLS，可通过导入行切换为 airPLS。

**输入、输出**：`INPUT_PATH` 指定原始 TIFF；`OUTPUT_PATH` 默认输出 `work/baseline/output/background.tif`；`CORRECTED_OUTPUT_PATH` 输出同目录的 `corrected.tif`；`CORRECTED_CSV_PATH` 输出 `work/baseline/output/corrected_x0_y0.csv`，供对比绘图使用。未处理点为 `NaN`。

**需要修改的配置**：顶部路径、`BASELINE_METHOD`、`BASELINE_OPTIONS`、`READER_OPTIONS` 和 `Y_START/Y_END`、`X_START/X_END`；默认只处理 `(x=0, y=0)`。例如处理 `(x=5, y=3)` 时，设 `Y_START, Y_END = 3, 4`、`X_START, X_END = 5, 6`，并同步修改 CSV 点位 `CSV_X_COORDINATE/CSV_Y_COORDINATE` 和文件名。

## run.py

```bash
python work/baseline/run.py
```

**用途与方法**：原有逐点背景估计流程，默认 airPLS，默认处理全部空间点。

**输入、输出**：`INPUT_PATH` 默认 `input.tif`；在 `OUTPUT_DIR` 保存 `background.tif`、`corrected.tif`、`metadata.json`。不输出单点 CSV；Gaussian 拟合入口读取这里生成的 `corrected.tif`。

**需要修改的配置**：顶部读取器、算法、方法参数、位移范围和空间范围。路径和范围也可由 `--input`、`--output`、`--y-start`、`--y-end`、`--x-start`、`--x-end` 覆盖，其中 `--output` 指定目录。
