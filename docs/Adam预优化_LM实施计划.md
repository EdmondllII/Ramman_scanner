# Adam 预优化与 LM 精修实施计划

## 目标

在现有 LOPC 非线性最小二乘拟合之前增加一次可选的 Adam 预优化：

```text
当前初值
  -> Adam 梯度下降，寻找较好的参数区域
  -> 将 Adam 结果写回 lmfit Parameters
  -> 现有 leastsq/Levenberg-Marquardt 精修
```

本计划只针对 LOPC 实验路径。Lorentzian 拟合和 `work/fitting/run.py` 保持不变，默认行为仍然是直接使用现有 LM。

## 实施边界

- 不修改 `lmfit-py` 源码，也不把 Adam 塞进 `Model.fit()`。
- 不删除或替换现有 `lopc.fit()` 的 LM 路径。
- 不把 Adam 的结果直接当作最终结果；最终参数仍以 LM 返回值为准。
- 第一版不做小批量训练、GPU 调度或全空间点无条件 Adam。
- 只在显式开启时运行，例如 `optimizer="adam_then_lm"`。

## 第一阶段代码结构

新增项目模块：

```text
raman/fitting/adam_prefit.py
```

模块内部暂定分为三部分：

1. `lopc_torch(...)`

   用 PyTorch 运算重写当前 LOPC 正向函数。不能在这里调用 NumPy 版 `lopc()`，否则自动微分链会被切断。计算使用 `torch.float64`，并保留复数介电函数和 `imag(-1/epsilon)` 的现有定义。

2. 参数变换和边界处理

   Adam 优化无约束变量，再映射到物理参数：

   - 非负参数使用 `softplus`，例如 amplitude、omega_p、gamma_p、gamma_ph；
   - 有限区间参数使用 sigmoid 映射，例如把 omega_l 限制在 LOPC 窗口附近；
   - 不在每一步简单裁剪原始参数，以免在边界处产生不平滑梯度。

3. `adam_prefit_lopc(...)`

   接收 `x`、`y`、当前初值和物理边界，执行完整窗口上的 Adam 迭代，并返回：

   - 最优参数字典；
   - Adam 阶段的最终 loss 和最优 loss；
   - 迭代次数；
   - 是否出现 NaN/Inf。

## 与现有 LOPC 拟合的连接

在 `raman/fitting/lopc.py` 中增加一个可选的初值入口，而不是改变现有默认接口：

```python
fit(..., initial_values=None, optimizer="lm")
```

建议逻辑：

```text
建立当前 lmfit Parameters
  -> optimizer == "adam_then_lm" 时调用 adam_prefit_lopc
  -> 用 Adam 返回值更新 amplitude、omega_p、gamma_p、gamma_ph、omega_l
  -> 调用 model.fit(..., method="leastsq")
  -> 返回 LM 的 ModelResult
```

`optimizer="lm"` 或省略参数时，必须与当前结果完全一致。

`fit_scan.py` 只增加一个显式配置项，例如：

```python
LOPC_OPTIMIZER = "lm"
```

实验时改成 `"adam_then_lm"`。输出 CSV 之外，建议在诊断文件中记录 optimizer、Adam loss、LM chisqr、LM nfev 以及是否触发回退。

## Adam 阶段的初始配置

第一版使用保守配置，不追求训练速度：

- 全部 LOPC 窗口点参与 loss；
- loss 初步使用未加权 MSE；
- `torch.optim.Adam`；
- 使用 `float64`；
- 设置有限的最大步数和早停条件；
- 保存历史最优参数，而不是盲目使用最后一步参数；
- loss 或模型输出出现非有限值时立即回退到原始 LM 初值。

学习率、步数和边界需要通过单条 `(x=0, y=0)` 光谱先调试，再扩展到整个扫描立方体。第一版不同时引入鲁棒 loss、局部背景和多组随机初值，否则无法判断改善来自哪个改动。

## 验证标准

至少比较以下三条路径：

```text
A. 直接 LM
B. Adam -> LM
C. 多组 LM 初值（作为不依赖 Adam 的对照）
```

每条路径都比较：

- 最终 `chisqr` 和残差曲线；
- `omega_l`、`omega_p`、`gamma_p`、`gamma_ph` 是否撞边界；
- 更换初值后的参数稳定性；
- 拟合曲线是否实际改善，而不是只有参数数值变化；
- 单点耗时和全图总耗时。

判断规则：

- 曲线和参数都稳定：Adam 可能没有必要；
- 曲线明显改善且 LM 参数不再极端：Adam 作为预优化有效；
- 曲线相同但参数差异很大：仍是不可辨识问题，不是优化器问题；
- Adam 后 LM 仍撞边界：优先收紧物理边界或减少自由参数。

## PyTorch 环境复用方案

当前检查结果：

- `env1` 中的 Torch 是 `torch 2.13.0+cu130`，由 PyPI 安装；
- `Raman` 环境目前没有 Torch；
- Torch 不在 Conda 包缓存中；
- 两个环境的 Python 都是 CPython 3.14，但补丁版本分别为 3.14.6 和 3.14.7。

### 推荐：共享本地 wheel，不重复下载

Conda 环境之间不会自动共享 pip 已安装目录。正确做法是准备一个本地 wheelhouse，然后在 `Raman` 中从本地安装：

```powershell
conda run -n env1 python -m pip download --no-deps <torch-wheel-or-spec> -d D:\Edmon\wheelhouse
conda run -n Raman python -m pip install --no-index --find-links D:\Edmon\wheelhouse torch
```

如果安装包已经存在于 pip 缓存，也可以先用：

```powershell
conda run -n Raman python -m pip install --no-index --find-links <本地wheel目录> torch
```

这种方式只下载一次，但两个环境各自登记安装信息，升级和卸载互不破坏，最适合作为正式方案。当前检查到的 pip cache 没有列出 Torch wheel，因此现有 `env1\Lib\site-packages` 本身不能直接被 pip 当作安装源。

### 临时实验：用 `.pth` 直接让 Raman 找到 env1 的包

可以在 `Raman\Lib\site-packages` 放一个只包含下列路径的 `.pth` 文件：

```text
D:\Edmon\Miniconda\envs\env1\Lib\site-packages
```

这样 `Raman` 的 Python 进程会把 `env1` 的 site-packages 加入 `sys.path`，从而尝试直接导入 Torch。这不是安装：

- `pip list` 不会正确反映 Torch 属于 Raman；
- 删除或升级 `env1` 会影响 Raman；
- env1 的依赖版本可能污染 Raman；
- Torch 的 CUDA DLL 和 Python 版本必须实际测试；
- 只建议用于短期实验，不建议写入项目部署流程。

导入验证应使用：

```powershell
conda run -n Raman python -c "import torch; print(torch.__version__); print(torch.__file__)"
```

### 关于 Windows 硬链接

Windows 的硬链接只能针对单个文件，不能对整个目录建立硬链接。Torch 是包含大量 Python 文件、`.pyd` 扩展和 DLL 的目录树，逐文件建立硬链接既脆弱又会让两个环境共享同一 inode；任一环境升级或删除文件都可能破坏另一环境。

目录联接（junction）或符号链接可以实现目录级复用，但它们同样不是正常安装，且会把环境生命周期绑定在一起。因此不建议把 `env1\site-packages\torch` 直接联接到 `Raman`，除非只是临时验证。

## 实施顺序

1. 先加入 Torch 依赖并确认 `Raman` 环境能以 `float64` 导入和运行。
2. 用一条固定 LOPC 光谱验证 `lopc_torch()` 与 NumPy 版曲线一致。
3. 验证 Adam 的 loss 能下降且梯度保持有限。
4. 接入 `adam_then_lm`，保留直接 LM 基线。
5. 在 `(x=0, y=0)` 上比较 A/B/C 三条路径。
6. 只有确认单点有效且耗时可接受后，才扩展到空间扫描。

