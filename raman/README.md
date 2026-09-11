# raman

- `__init__.py`：定义 `raman` 包并导出公共数据类型。
- `data.py`：定义 `RamanData`，统一表示光谱、二维扫描图和 TIFF 光谱立方体。
- `output.py`：保存处理后的光谱、基线、拟合曲线和拟合参数，包括逐空间点的结果。
- `io/`：提供 TXT 和 TIFF 数据读取方法。
- `baseline/`：提供基线矫正方法。
- `fitting/`：提供峰检测和线形拟合方法。
- `reconstruction/`：提供与拟合参数一致的 Gaussian、Lorentzian 单谱重建方法。

扫描区域遍历、结果文件和绘图由项目根目录的 `work/` 包负责；`raman/`
中的方法只接收一条光谱及其坐标，不处理空间循环。
