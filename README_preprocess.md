# 处理流程说明

旧的根目录 `main.py` 已取消。当前流程按步骤运行 `work/` 中的入口：

```bash
python work/baseline/baseline_scan.py
python work/fitting/fit_scan.py
python work/reconstruction/reconstruct_spectrum.py
```

基线和拟合入口顶部直接选择方法、参数、路径和逐点范围；重建入口顶部直接选择重建线型和参数列映射。各步骤的职责、输入和输出见 [`work/README.md`](work/README.md) 与 [`docs/workflow_design.md`](docs/workflow_design.md)。
