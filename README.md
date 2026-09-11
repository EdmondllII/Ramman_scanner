# 拉曼扫描数据分析

这是一个拉曼扫描数据处理程序。算法位于 `raman/`，面向实际数据的独立步骤位于 `work/`。安装依赖后：
```text
conda activate raman

python -m pip install -r requirements.txt
python -m work.baseline.run --input input.tif
python -m work.fitting.run --input input.tif
```

## 文件说明

- `work/baseline/run.py`：逐空间点估计背景，输出 `background.tif` 和元数据。
- `work/fitting/run.py`：逐空间点检测峰并拟合，输出长表 `fit_parameters.csv` 和元数据。
- `work/reconstruction/`：从参数重建分峰/总谱，并提供谱线加减运算。
- `work/visualization/`：只读取已有结果并绘图。
- `raman/io/`：TXT 与 TIFF 数据读取实现；可用读取器在 `raman/io/__init__.py` 中列出。
- `raman/baseline/`：AsLS 与 airPLS 基线矫正实现；可用方法在 `raman/baseline/__init__.py` 中列出。
- `raman/fitting/`：单条光谱的峰检测和 Gaussian 拟合实现；可用方法在 `raman/fitting/__init__.py` 中列出。
- `raman/reconstruction/`：Gaussian、Lorentzian 单条谱线重建函数。

每个工作脚本顶部都暴露了读取器、算法和参数常量，可直接修改以选择方法；脚本也支持命令行参数覆盖输入、输出和空间范围。TIFF 统一按 `(y, x, Raman shift)` 处理。
