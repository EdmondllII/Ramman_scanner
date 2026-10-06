# 拉曼扫描工作流程

这是科研分析脚本，不设置总入口，也不设置配置框架。`raman/` 封装单条光谱算法，`work/` 中的每个脚本负责一次明确的实际操作：读取数据、必要时循环空间点、调用算法、保存结果。

## 文件结构

```text
work/
├── baseline/
│   └── baseline_scan.py
├── fitting/
│   └── fit_scan.py
├── reconstruction/
│   ├── reconstruct_spectrum.py
│   ├── add_spectra.py
│   └── subtract_spectra.py
├── evaluation/
│   └── evaluate_fit.py
└── visualization/
    ├── plot_single_spectrum.py
    ├── plot_spectra_comparison.py
    └── plot_parameter_heatmap.py
```

每个脚本顶部直接写路径、参数和方法，执行方式统一为：

```bash
python work/目录/脚本.py
```

## 基线

`baseline_scan.py` 使用二重循环逐点调用一个 `raman.baseline` 方法，并保存 `background.tif` 和已经扣除背景的 `corrected.tif`。后者是 fitting 工作流的输入。

```python
from raman.baseline import airpls as BASELINE_METHOD  # 改成 asls 即可换方法

for y in range(Y_START, Y_END):
    for x in range(X_START, X_END):
        corrected, background = BASELINE_METHOD(axis, spectrum, **OPTIONS)
```

脚本中 `Y_END` 或 `X_END` 为 `None` 时处理到数据边界；单点设置为相邻整数，例如 `Y_START, Y_END = 3, 4`。

## 拟合

`fit_scan.py` 使用相同的二重循环，读取已经完成背景扣除的 TIFF；每个点直接调用峰检测和拟合函数，只保存逐点逐峰的拟合参数表。单条校正 CSV 可作为单点输入。

```python
from raman.fitting import gaussian as FIT_METHOD  # 改成 lorentzian 或 voigt 即可换线型

for y in range(Y_START, Y_END):
    for x in range(X_START, X_END):
        centers = PEAK_METHOD(axis, corrected, **PEAK_OPTIONS)
        result = FIT_METHOD(axis, corrected, centers=centers, **FIT_OPTIONS)
```

如果是另一种拟合流程，复制 `fit_scan.py`，只修改导入和调用部分即可。

## 重建和谱线运算

`reconstruct_spectrum.py` 读取参数表，按顶部的 `X_COORDINATE`、`Y_COORDINATE` 和 `PARAMETER_MAPPING` 选择参数，再调用 `RECONSTRUCT_METHOD` 叠加分峰。Gaussian、Lorentzian 与 Voigt 的切换只需修改一行导入。Voigt 特有的 `gamma` 会保存在拟合参数表中并用于重建。`add_spectra.py` 和 `subtract_spectra.py` 各自只做一件事。

## 评估和可视化

`evaluate_fit.py` 比较两条已对齐的 CSV 光谱并保存指标。三个可视化脚本分别绘制单点谱、多谱线对比和参数热力图；它们都直接读取文件并保存图片。

## 信息保存

- 原始扫描数据和背景使用 TIFF。
- 单条光谱和拟合参数使用 CSV。
- 评估指标使用 JSON。
- 图片使用 PNG 等常见格式。

简化脚本不会改变算法结果或核心数据。算法仍集中在 `raman/`，实验步骤集中在 `work/`，方法、参数、循环范围和输出位置都能在当前脚本中直接看到。
