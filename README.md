# 拉曼扫描数据分析

这是一个拉曼扫描数据处理程序。算法位于 `raman/`，面向实际数据的独立步骤位于 `work/`。安装依赖后：
```text
conda activate raman

python -m pip install -r requirements.txt
python work/baseline/baseline_scan.py
python work/fitting/fit_scan.py
```

上面两条命令分别生成背景和逐点峰拟合参数。重建、拟合效果评估、光谱加减和绘图也都是独立脚本；完整的文件职责、参数说明和可复制命令见 [`work/README.md`](work/README.md)，各子目录下的 README 还提供对应步骤的细节。

项目设计、工作流、数据约定、数学与物理模型、原理调研和阶段报告见 [`docs/README.md`](docs/README.md)，从该入口可以按主题继续阅读。

## 文件说明

- `work/baseline/baseline_scan.py`：逐空间点估计背景，输出 `background.tif`（[说明](work/baseline/README.md)）。
- `work/fitting/fit_scan.py`：逐空间点检测峰并拟合，输出长表 `fit_parameters.csv`（[说明](work/fitting/README.md)）。
- `work/reconstruction/`：从参数重建分峰/总谱，并提供谱线加减运算（[说明](work/reconstruction/README.md)）。
- `work/evaluation/`：比较目标拉曼谱和拟合结果谱，输出整体及快速变化部分的拟合指标（[说明](work/evaluation/README.md)）。
- `work/visualization/`：只读取已有结果并绘图（[说明](work/visualization/README.md)）。
- `raman/io/`：TXT 与 TIFF 数据读取实现；可用读取器在 `raman/io/__init__.py` 中列出。
- `raman/baseline/`：AsLS 与 airPLS 基线矫正实现；可用方法在 `raman/baseline/__init__.py` 中列出。
- `raman/fitting/`：单条光谱的峰检测及 Gaussian、Lorentzian、Voigt 拟合；可用方法在 `raman/fitting/__init__.py` 中列出。
- `raman/reconstruction/`：Gaussian、Lorentzian、Voigt 单条谱线重建函数。

基线、拟合和重建脚本在顶部直接写出读取器、算法、参数、路径和循环范围，修改后运行 `python xxx.py` 即可。TIFF 统一按 `(y, x, Raman shift)` 处理。
