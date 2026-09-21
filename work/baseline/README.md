# 基线估计

`run.py` 保留原有的基线工作流。新增的 `baseline_scan.py` 独立执行 airPLS，同时保存 `background.tif`、已经扣除背景的 `corrected.tif`，并额外将指定空间点的校正谱保存为两列 CSV，不替换 `run.py`。

```bash
python work/baseline/baseline_scan.py
```

脚本顶部的 `BASELINE_METHOD` 用于选择方法，例如将 `airpls` 改为 `asls`；`BASELINE_OPTIONS` 是方法参数；`INPUT_PATH` 和 `OUTPUT_PATH` 是输入输出；`Y_START/Y_END`、`X_START/X_END` 是扫描范围。只处理 `(x=5, y=3)` 时设置 `Y_START, Y_END = 3, 4` 和 `X_START, X_END = 5, 6`。
