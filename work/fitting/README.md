# 峰检测与拟合

`run.py` 保留原有的逐点拟合工作流。新增的 `fit_scan.py` 只读取已经完成背景扣除的 TIFF 或单条 CSV，在 735 cm^-1 附近使用 LOPC、其余峰使用 Lorentzian，不替换 `run.py`。

```bash
python work/fitting/run.py
python work/fitting/fit_scan.py
```

脚本顶部的 `PEAK_OPTIONS`、`FIT_OPTIONS`、`LOPC_RANGE` 和 `LOPC_OPTIONS` 分别控制寻峰、Lorentzian 和 LOPC；`INPUT_PATH` 和 `OUTPUT_PATH` 是文件位置；`Y_START/Y_END`、`X_START/X_END` 是 TIFF 扫描范围。TIFF 每个空间点独立拟合，CSV 按单点 `(x=0, y=0)` 处理，不求平均谱。

新脚本输出 `fit_parameters_lopc.csv`，其中 `model` 列标记 `lorentzian` 或 `lopc`。Lorentzian 行使用 `position`、`amplitude`、`sigma`、`fwhm`；LOPC 行使用 `position`（拟合曲线最大值）、`amplitude`、`omega_l`、`omega_p`、`gamma_p`、`gamma_ph`、`omega_t`、`epsilon_inf`。不适用的列写为 `NaN`；其中 `omega_l` 是 LOPC 参数，不等同于观测曲线最大值。
# LOPC Adam 预优化实验

`fit_scan.py` 的 LOPC 实验路径当前使用 `adam_then_lm`：先从自动寻峰和固定初值开始，用 `env1` 环境中的 PyTorch Adam 搜索参数区域，再把结果交给现有 lmfit `leastsq`/Levenberg-Marquardt 精修。普通 Lorentzian 峰和 `run.py` 不受影响。

Adam 通过硬路径 `D:\Edmon\Miniconda\envs\env1\Lib\site-packages` 导入 Torch；如果需要关闭预优化，将 `LOPC_OPTIONS["optimizer"]` 改为 `"lm"`。最终参数仍以 LM 返回结果为准。
