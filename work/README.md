# work 工作脚本

`work/` 中的每个 `.py` 文件都是一个可以直接运行的实验脚本。打开脚本顶部修改路径、参数和范围，然后在项目根目录执行：

```bash
python work/baseline/baseline_scan.py
python work/fitting/fit_scan.py
python work/reconstruction/reconstruct_spectrum.py
python work/evaluation/evaluate_fit.py
```

## 目录

`baseline/`：`baseline_scan.py` 逐点调用 `raman.baseline` 中的一个基线方法，输出 `background.tif` 和已经扣除背景的 `corrected.tif`；`README.md` 说明用法；`output/` 保存结果。

`fitting/`：`fit_scan.py` 读取已经完成背景扣除的 TIFF 或单条 CSV，调用峰检测与拟合方法，输出拟合参数表；`README.md` 说明用法；`output/` 保存结果。

`reconstruction/`：`reconstruct_spectrum.py` 根据参数表重建指定点的光谱；`add_spectra.py` 相加两条光谱；`subtract_spectra.py` 相减两条光谱；`README.md` 说明用法；`output/` 保存结果。

`evaluation/`：`evaluate_current_fit.py` 直接评估当前校正谱和混合拟合参数，`evaluate_fit.py` 读取两条 CSV 光谱做通用比较；`README.md` 和 `fit_evaluation_and_GaN_attribution.md` 说明用法及峰归因边界；`output/` 保存结果。

`visualization/`：`plot_single_spectrum.py` 绘制单点原始/背景/校正谱；`plot_spectra_comparison.py` 对比多条光谱；`plot_parameter_heatmap.py` 绘制参数热力图；`README.md` 说明用法；`output/` 保存图片。

每个脚本都直接调用 `raman/` 的单条光谱接口。若要更换方法，修改脚本中的导入行；若要使用完全不同的方法，复制脚本并修改那一行。扫描脚本中的 `Y_START/Y_END` 和 `X_START/X_END` 控制循环范围，单点只需把范围改成相邻的两个整数。
