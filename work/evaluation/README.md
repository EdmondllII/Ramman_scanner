# 拟合效果评估

本目录评估已有结果，不执行拟合。LOPC 混合模型使用 `evaluate_current_fit.py`；两条外部 CSV 的通用比较使用 `evaluate_fit.py`。所有命令在项目根目录执行。

历史分析见 [拟合效果与 GaN 峰归因](../../docs/reports/fit_evaluation_and_GaN_attribution.md) 和 [拟合归因与振幅物理约束](../../docs/reports/拟合归因与振幅物理约束_2026-09-18.md)。这些记录中的数值对应当时结果，重新评估后应查看新输出。

## evaluate_current_fit.py

```bash
python work/evaluation/evaluate_current_fit.py
```

**用途与模型**：从参数表重建指定点的 Lorentzian + LOPC 混合谱，按 lmfit 残差定义计算全谱、各模型实际拟合区间及 LOPC 窗口内总重建指标，并诊断负振幅和异常宽分量。

**输入、输出**：`SPECTRUM_PATH` 默认 `work/baseline/output/corrected.tif`，`PARAMETERS_PATH` 默认 `work/fitting/output/fit_parameters_lopc.csv`；在 `OUTPUT_DIR`（默认 `work/evaluation/output`）输出 `fit_metrics_x0_y0.json`、`fit_report_x0_y0.txt`、`fit_spectrum_x0_y0.csv`。文件名随点位变化；CSV 包含校正谱、总重建谱、模型分量及残差。

**需要修改的配置**：顶部路径、`X_COORDINATE/Y_COORDINATE`、`READER_OPTIONS` 和 `LOPC_RANGE`；坐标、位移范围和 LOPC 窗口应与拟合设置一致，默认评估 `(x=0, y=0)`。

参数表不保存 lmfit `ModelResult`，无法恢复原始协方差、收敛状态和优化次数。重算的 AIC/BIC、redchi 是诊断指标，不能代替原始优化器报告。

## evaluate_fit.py

```bash
python work/evaluation/evaluate_fit.py
```

**用途与方法**：比较两条光谱的残差和梯度差异，输出整体与快速变化部分的拟合指标。

**输入、输出**：`TARGET_PATH` 默认 `target.csv`，`FITTED_PATH` 默认 `fitted.csv`；均为两列 CSV 且 Raman 位移轴相同。`OUTPUT_PATH` 默认 `work/evaluation/output/fit_metrics.json`。

**需要修改的配置**：顶部三个路径。比较当前校正谱与重建谱时，将输入分别改为 `work/visualization/output/corrected_x0_y0.csv` 和 `work/reconstruction/output/reconstructed.csv`。此脚本不自动读取混合拟合参数表。
