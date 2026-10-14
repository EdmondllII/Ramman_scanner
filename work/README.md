# work 工作脚本

`work/` 中的每个 `.py` 文件都是一个可以直接运行的实验脚本。打开脚本顶部修改路径、参数和范围，然后在项目根目录执行：

```bash
python work/baseline/baseline_scan.py
python work/fitting/fit_scan.py
python work/reconstruction/reconstruct_spectrum.py
python work/visualization/plot_spectra_comparison.py
python work/evaluation/evaluate_current_fit.py
```

完整 Faust–Henry A 项使用独立实验路径，共用已有基线校正结果：

```bash
python work/fitting/fit_scan_fh.py
python work/reconstruction/reconstruct_spectrum_fh.py
python work/visualization/plot_spectra_comparison_fh.py
python work/evaluation/evaluate_current_fit_fh.py
```

Gaussian 仪器卷积的完整 A 项使用另一条独立路径；`sigma_inst` 初值为 1.0 cm⁻¹，当前 `vary_sigma_inst=True`，Adam 和 LM 均优化。改为 False 恢复固定宽度版本，配置写在 `fit_scan_fh_convolved.py` 顶部：

```bash
python work/fitting/fit_scan_fh_convolved.py
python work/reconstruction/reconstruct_spectrum_fh_convolved.py
python work/visualization/plot_spectra_comparison_fh_convolved.py
python work/evaluation/evaluate_current_fit_fh_convolved.py
```

参数、重建谱、图片和评估均输出到独立文件。模型细节与可拟合的 `C` 见 [拟合说明](fitting/README.md#fit_scan_fhpy)。

每次运行须对齐各阶段的路径、位移轴和空间点：基线与拟合的处理范围应覆盖待重建点，绘图与评估读取本轮重建输出。当前 baseline 和未卷积 FH 拟合处理全图；卷积 FH 拟合、重建、绘图和评估默认原点。未卷积 FH 重建为三维 TIFF，绘图和评估按配置提取单点；卷积 FH 重建仍为单点 CSV。切换空间点时同步修改相应坐标及 baseline 的 CSV 导出点。

## 目录

`baseline/`：`baseline_scan.py` 逐点调用 `raman.baseline` 中的一个基线方法，输出 `background.tif` 和已经扣除背景的 `corrected.tif`；`README.md` 说明用法；`output/` 保存结果。

`fitting/`：`fit_scan.py` 读取已经完成背景扣除的 TIFF 或单条 CSV，调用峰检测与拟合方法，输出拟合参数表；`README.md` 说明用法；`output/` 保存结果。

`reconstruction/`：`reconstruct_spectrum.py` 根据参数表重建指定点的光谱；`add_spectra.py` 相加两条光谱；`subtract_spectra.py` 相减两条光谱；`README.md` 说明用法；`output/` 保存结果。

`evaluation/`：所有入口只读取目标谱与已重建谱，输出误差指标和残差；`evaluate_current_fit.py`、`evaluate_current_fit_fh.py` 分别配置普通路径与完整 A 项路径，`evaluate_fit.py` 提供通用比较；[README.md](evaluation/README.md) 按脚本说明用法；历史拟合评估、峰归因与振幅物理约束分析见 [阶段记录](../docs/reports/README.md)；`output/` 保存结果。

`visualization/`：`plot_single_spectrum.py` 绘制单点原始/背景/校正谱；`plot_spectra_comparison.py` 对比多条光谱；`plot_parameter_heatmap.py` 绘制参数热力图；`README.md` 说明用法；`output/` 保存图片。

每个脚本都直接调用 `raman/` 的单条光谱接口。若要更换方法，修改脚本中的导入行；若要使用完全不同的方法，复制脚本并修改那一行。扫描脚本中的 `Y_START/Y_END` 和 `X_START/X_END` 控制循环范围，单点只需把范围改成相邻的两个整数。
