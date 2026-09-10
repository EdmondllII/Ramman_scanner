# io

- `__init__.py`：集中导出当前可用的数据读取方法。
- `txt_reader.py`：读取 TXT、CSV 等数值文本，支持两列光谱和二维扫描矩阵。
- `tiff_reader.py`：读取三维 TIFF 光谱立方体，并统一为 `(y, x, Raman shift)` 格式。
