# fitting

- `__init__.py`：集中导出当前可用的单条光谱处理、峰检测和拟合方法。
- `peak_detection.py`：处理单条光谱并检测峰位置；光谱立方体由 `work/fitting/fit_scan.py` 逐空间点调用该方法。
- `gaussian.py`：使用 `lmfit` 的 Gaussian 模型执行单峰或多峰拟合。
- `lorentzian.py`：使用相同接口执行 Lorentzian 拟合，可在工作脚本顶部替换。
- `voigt.py`：封装 `lmfit.models.VoigtModel`，使用相同接口执行 Voigt 拟合。
- `lopc.py`：使用 \(A_{\mathrm{FH}}=1\) 的介电损耗函数执行单峰 LOPC 拟合；该模型参数相关性较强，应传入物理合理的 `omega_p`、`gamma_p` 和 `gamma_ph` 初值。

`voigt(..., gamma=None)` 沿用 lmfit 默认的 `gamma=sigma` 约束；显式传入 `gamma` 时，该参数作为独立的 Lorentzian 半高半宽参与拟合。
# LOPC Adam 预优化

`lopc.fit(..., optimizer="adam_then_lm")` 会先调用 `adam_prefit.py` 中的 Torch Adam，再将物理参数作为 lmfit `leastsq` 的初值。默认 `optimizer="lm"` 保持原有行为；Adam 仅用于 LOPC，不参与普通 Lorentzian 拟合。

寻峰要求候选点高度 `>= 0`，不会截断输入光谱中的负值。Gaussian、Lorentzian、Voigt 和 LOPC 的拟合振幅均设非负下界；普通峰的正宽度与非负面积共同保证峰高非负。

LOPC 的 Adam 和 LM 阶段均不设人为参数上限，也不将 `omega_l` 限制在数据窗口内；保留频率、阻尼及介电常数的物理正值要求。`omega_t` 和 `epsilon_inf` 默认仍作为固定材料参数，由 `vary_omega_t` 和 `vary_epsilon_inf` 控制是否参与 LM 优化。
