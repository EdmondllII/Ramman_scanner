# 拟合效果评估

`evaluate_current_fit.py` 使用当前 baseline 和 fitting 输出，重建指定空间点的混合模型，并用 lmfit 的残差平方和定义计算全谱、Lorentzian 区间和 LOPC 区间指标。`evaluate_fit.py` 保留为两条外部 CSV 的通用比较脚本。`output/` 保存结果。

当前结果和 GaN LED 候选峰的分析见 [`fit_evaluation_and_GaN_attribution.md`](fit_evaluation_and_GaN_attribution.md)；振幅正值约束与负振幅使用边界见 [`拟合归因与振幅物理约束_2026-09-18.md`](拟合归因与振幅物理约束_2026-09-18.md)。

评估当前 `(x=0,y=0)`：

```powershell
D:\Edmon\Miniconda\envs\Raman\python.exe .\work\evaluation\evaluate_current_fit.py
```

脚本顶部可修改 `SPECTRUM_PATH`、`PARAMETERS_PATH`、空间坐标和 `LOPC_RANGE`。

```bash
python work/evaluation/evaluate_fit.py
```

脚本顶部修改 `TARGET_PATH`、`FITTED_PATH` 和 `OUTPUT_PATH`。两条输入必须是相同 Raman 位移轴的两列 CSV。
