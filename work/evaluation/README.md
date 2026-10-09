# 拟合效果评估

本目录只比较已有目标光谱与已有拟合（重建）光谱。输入为两条位移轴一致的两列 CSV，不读取拟合参数，不重建，不拟合，不绘图，不执行物理归因。当前目标谱为基线校正结果，应先完成拟合和重建。所有命令在项目根目录执行。

历史分析见 [拟合效果与 GaN 峰归因](../../docs/reports/fit_evaluation_and_GaN_attribution.md) 和 [拟合归因与振幅物理约束](../../docs/reports/拟合归因与振幅物理约束_2026-09-18.md)。历史报告中的分量诊断与旧指标不属于当前评估接口。

## evaluate_current_fit.py

```bash
python work/evaluation/evaluate_current_fit.py
```

**用途与方法**：比较当前目标谱和已重建总谱，计算全谱与配置区间的未加权误差。算法不知道拟合使用的是哪种模型。

**输入、输出**：`TARGET_PATH` 默认 `work/baseline/output/corrected_x0_y0.csv`；`FITTED_PATH` 默认 `work/reconstruction/output/reconstructed.csv`。输出目录为 `work/evaluation/output/`，包含 `fit_metrics_x0_y0.json`、`fit_report_x0_y0.txt`、`fit_spectrum_x0_y0.csv`。

**需要修改的配置**：顶部输入路径、`OUTPUT_DIR`、文件名标签 `OUTPUT_STEM`、可选区间 `REGIONS`。默认另评估 720–750 cm⁻¹ 区间；设置 `REGIONS={}` 只评估全谱。区间只对两条已有曲线切片，不计算模型分量。

## evaluate_current_fit_fh.py

```bash
python work/evaluation/evaluate_current_fit_fh.py
```

**用途与方法**：完整 A 项实验的评估入口，与普通入口使用同一比较函数，不读取 C 或计算 Faust–Henry 因子。

**输入、输出**：目标谱仍为 `corrected_x0_y0.csv`，拟合谱为 `work/reconstruction/output/reconstructed_fh.csv`。指标、报告和残差 CSV 写入 `work/evaluation/output/lopc_fh/`。

**需要修改的配置**：顶部两条输入路径、输出目录、文件名标签与 `REGIONS`。先运行 `reconstruct_spectrum_fh.py`，确保重建数据是最新结果。

## evaluate_current_fit_fh_convolved.py

```bash
python work/evaluation/evaluate_current_fit_fh_convolved.py
```

**用途与方法**：比较校正谱与 Gaussian 仪器卷积完整 A 项的已有重建谱；复用同一未加权光谱比较函数，不读取参数或重新计算卷积。

**输入、输出**：目标谱为 `corrected_x0_y0.csv`，拟合谱为 `work/reconstruction/output/reconstructed_fh_convolved.csv`；指标、报告和残差写入 `work/evaluation/output/lopc_fh_convolved/`。

**需要修改的配置**：顶部两条输入路径、输出目录、文件名标签与 `REGIONS`。先运行 `reconstruct_spectrum_fh_convolved.py`。

## evaluate_fit.py

```bash
python work/evaluation/evaluate_fit.py
```

**用途与方法**：通用两条光谱比较，也是上述入口调用的公共文件处理函数。纯误差算法位于 `raman/evaluation.py`。

**输入、输出**：默认读取 `target.csv` 和 `fitted.csv`，保存 `work/evaluation/output/fit_metrics.json`，同时保存 `fit_report.txt` 和 `fit_spectrum.csv`。

**需要修改的配置**：顶部 `TARGET_PATH`、`FITTED_PATH`、`OUTPUT_PATH`。两条光谱必须具有相同位移轴，不自动插值；同步排除无效点，剩余位移须严格递增。

JSON 的 `metrics` 包含 `full_spectrum` 及可选区间，每组提供平方误差和、RMSE、MAE、最大绝对残差、R² 和梯度误差。残差 CSV 为 `raman_shift,target,fitted,residual`。不再输出分量、候选归属、参数诊断、AIC/BIC 或按自由度计算的 redchi；这些需要模型或参数信息，不能仅从两条曲线得到。所有指标保持未加权，便于比较不同拟合策略。
