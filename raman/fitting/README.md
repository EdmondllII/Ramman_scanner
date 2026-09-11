# fitting

- `__init__.py`：集中导出当前可用的单条光谱处理、峰检测和拟合方法。
- `peak_detection.py`：处理单条光谱并检测峰位置；光谱立方体由 `work/fitting/run.py` 逐空间点调用该方法。
- `gaussian.py`：使用 `lmfit` 的 Gaussian 模型执行单峰或多峰拟合。
- `lorentzian.py`：使用相同接口执行 Lorentzian 拟合，可在工作脚本顶部替换。
