# io

- `__init__.py`：集中导出当前可用的数据读取方法。
- `spectrum_reader.py`：读取两列 CSV 光谱，供重建和可视化脚本复用。
- `txt_reader.py`：读取 TXT、CSV 等数值文本，支持两列光谱和二维扫描矩阵。
- `tiff_reader.py`：读取三维 TIFF 光谱立方体，并统一为 `(y, x, Raman shift)` 格式。

本子包只负责文件读取和数据解析，不负责基线、拟合、重建、评估或输出文件。
