# reconstruction

- `__init__.py`：集中导出单条光谱的重建方法。
- `gaussian.py`：根据 Gaussian 参数重建单条光谱。
- `lorentzian.py`：根据 Lorentzian 参数重建单条光谱。
- `voigt.py`：根据 Voigt 的 `amplitude`、`center`、`sigma` 和 `gamma` 重建单条光谱。
- `lopc.py`：根据 \(A_{\mathrm{FH}}=1\) 的 LOPC 参数重建单条光谱。

本目录只处理一条光谱，不负责扫描空间点遍历、参数文件读取或结果保存。
