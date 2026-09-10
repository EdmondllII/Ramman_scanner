# lmfit-py：数学与物理原理调研

## 0. 调研范围

当前工作区没有 `lmfit-py/` 目录，也没有安装 `lmfit`。因此本文依据官方仓库 `lmfit/lmfit-py` 的源码与文档临时副本整理；报告描述的是项目的核心机制，不声称当前工作区存在该源码。lmfit 是通用拟合框架，不专属于 Raman 光谱。

## 1. 物理建模观点：把实验量写成参数化正向模型

lmfit 假定观测可写为

\[
y_i = f(x_i;\theta) + \varepsilon_i
\]

其中 \(f\) 是用户给出的物理/经验正向模型，\(\theta\) 是有名字的参数。框架本身不决定 \(f\) 的物理含义；它负责在给定模型族中寻找参数、表达约束并评估不确定度。

对 Raman 光谱，常见写法是“背景 + 峰的叠加”

\[
I(\nu) = b(\nu;\beta)
       + \sum_j A_j L_j(\nu;\mu_j,\operatorname{width}_j,\ldots)
\]

这里 \(b\) 可是常数、低阶多项式或样条，\(L_j\) 是峰形。这个结构把可解释参数（峰位、面积、宽度、偏斜度）直接连接到光谱特征，但峰形是否对应真实展宽机理需要使用者判断。

## 2. 目标函数与统计假设

### 2.1 加权非线性最小二乘

`Model.fit` 的默认残差是

\[
r_i(\theta) = w_i\bigl[y_i-f(x_i;\theta)\bigr]
\]

并最小化

\[
\chi^2(\theta) = \sum_i r_i(\theta)^2
\]

若 \(w_i=1/\sigma_i\)，则这是独立高斯测量误差下的负对数似然（略去常数）。因此权重必须与误差模型一致；任意“让曲线好看”的权重会改变统计解释。残差也可以是标量，或交给 `reduce_fcn` 使用非平方损失；内置的 Cauchy 对数似然对离群点更鲁棒。

### 2.2 复数与缺失值

复数残差被拆为实部和虚部两个实数分量。`nan_policy` 可选择报错、传播或删除缺失点；删除会改变有效数据数 \(N\)，进而影响自由度和不确定度。

## 3. Parameter：把约束从目标函数中分离

每个 `Parameter` 至少包含当前值 `value`、是否参与拟合 `vary`、下/上界 `min/max` 以及表达式约束 `expr`。例如

\[
\operatorname{FWHM} = 2.3548200\,\sigma
\]

可以作为派生参数，而不是独立变量。这样“固定哪一个量、哪些量有界、参数之间的代数关系”都在模型外部表达，目标函数仍保持物理形式。

有限边界通过内部变量变换交给无约束求解器。双边界的典型形式是

\[
p = p_{\min} + \frac{\bigl(\sin(u)+1\bigr)(p_{\max}-p_{\min})}{2}
\]

单边界使用平方根变换。优化器实际改变 \(u\)，回调模型时再转换成物理参数 \(p\)。这保证了边界，但在最优点贴近边界时，灵敏度和协方差近似会变差。

## 4. 优化算法与局部几何

默认方法是基于 MINPACK 的 Levenberg--Marquardt（`leastsq`）；也可使用 SciPy 的 trust-region `least_squares`、Nelder--Mead、Powell、L-BFGS-B、差分进化、basinhopping 等。

在最小二乘问题中，令 \(J_{ij}=\partial r_i/\partial\theta_j\)。LM 在每一步近似求解

\[
\bigl(J^\mathsf{T}J+\lambda_{\mathrm{LM}}I\bigr)\Delta\theta
= -J^\mathsf{T}r
\]

在梯度下降和 Gauss--Newton 之间切换。它快速但只保证找到局部极小点；多峰、强相关参数和差的初值会导致不同结果。全局算法可以帮助找初值，却通常不能替代局部精修和可辨识性检查。

## 5. 内置峰形及其物理解释

lmfit 的 `models.py` 提供归一化峰形，`amplitude` 通常代表曲线面积，`center` 是中心位置，`sigma` 是宽度参数。这种统一参数化方便比较模型。

### 5.1 Gaussian

\[
\begin{aligned}
G(x) &= \frac{A}{\sigma\sqrt{2\pi}}
\exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right), \\
\operatorname{FWHM} &= 2\sqrt{2\ln 2}\,\sigma.
\end{aligned}
\]

高斯形常用于许多独立小扰动的卷积极限，也常作为仪器分辨函数或非均匀性展宽的经验近似。

### 5.2 Lorentzian

\[
\begin{aligned}
L(x) &= \frac{A}{\pi}\,
\frac{\sigma}{(x-\mu)^2+\sigma^2}, \\
\operatorname{FWHM} &= 2\sigma.
\end{aligned}
\]

洛伦兹尾部可与有限寿命导致的均匀展宽联系起来，但只有在相应动力学假设成立时才有该物理解释。

### 5.3 Voigt 与 pseudo-Voigt

Voigt 是高斯和洛伦兹的卷积：

\[
\begin{aligned}
V(x) &= \frac{A\,\operatorname{Re}[w(z)]}{\sigma\sqrt{2\pi}}, \\
z &= \frac{x-\mu+i\gamma}{\sigma\sqrt{2}}.
\end{aligned}
\]

其中 \(w\) 是 Faddeeva 函数。它适合同时存在非均匀（Gaussian）和均匀（Lorentzian）展宽的情形。pseudo-Voigt 用共享中心和 \(\operatorname{FWHM}\) 的高斯/洛伦兹加权和近似 Voigt，`fraction` 在 0 到 1 之间。

其它内置模型（指数、幂律、阻尼振子、热分布、偏斜峰、样条等）都是可复用的函数族；它们是否代表 Raman 的声子占据、荧光衰减或仪器响应，取决于用户提供的实验解释。

## 6. Model 与复合模型

`Model(func)` 从 Python 函数签名推断参数名和自变量，并自动构造残差。两个模型可通过加法、乘法或标量组合成复合模型，例如

\[
I(\nu) = \operatorname{Gaussian}(\nu)
       + \operatorname{LinearBackground}(\nu)
\]

参数名前缀用于避免不同峰的 `center`、`sigma` 重名。复合模型的数学本质仍是同一个联合最小二乘问题；它不会自动解决峰数选择、峰间物理耦合或参数可辨识性。

## 7. 不确定度、相关性与模型比较

### 7.1 局部协方差

在最优点附近线性化残差，内部空间的协方差近似为

\[
\begin{aligned}
\operatorname{Cov}(\theta) &\approx
\bigl(J^\mathsf{T}J\bigr)^{-1}\,\chi^2_{\mathrm{red}}, \\
\chi^2_{\mathrm{red}} &= \frac{\chi^2}{N-P}.
\end{aligned}
\]

源码再用边界变换的梯度把协方差映射回外部参数，并报告 `stderr` 和相关系数。若 \(J^\mathsf{T}J\) 奇异，通常意味着参数退化、峰重叠或数据不足，此时标准误差可能为 `None` 或没有可靠意义。

### 7.2 置信区间与贝叶斯采样

`conf_interval` 通过固定一个参数、重新拟合其余参数，并用 F 检验比较 \(\chi^2\) 的变化，得到非对称置信区间。这比单纯使用 Hessian 更能处理强非线性。若使用 `emcee`，则是在参数空间中采样后验分布，需要明确先验和似然，不能把采样区间与局部标准误差混为一谈。

### 7.3 AIC/BIC

在高斯误差的近似下，源码使用

\[
\begin{aligned}
\operatorname{AIC} &= N\log\!\left(\frac{\chi^2}{N}\right)+2P, \\
\operatorname{BIC} &= N\log\!\left(\frac{\chi^2}{N}\right)+P\log N.
\end{aligned}
\]

其中 \(P\) 是可变参数数。它们用于在拟合优度和模型复杂度之间折衷，不是证明某个峰形具有更真实的微观物理。

## 8. 对 Raman 拟合的实际边界

1. 峰面积只有在基线、波数刻度、响应校正和峰间重叠处理正确时才可作相对定量；`amplitude` 的“面积”是函数归一化的数学属性。
2. Gaussian/Lorentzian/Voigt 是线形假设，不会自动编码 Raman 选择定则、偏振、温度、应力或仪器函数。若有理论线形，应通过自定义 `Model` 写入。
3. 峰位、宽度和面积常高度相关；应检查相关矩阵、profile 区间或后验，而不是只看拟合曲线和单个 `stderr`。
4. 最小二乘默认把误差看成独立同分布；CCD 的 Poisson 噪声、基线系统误差和谱点相关性需要通过权重、协方差白化或自定义似然显式处理。
5. 边界、固定参数和表达式约束改变有效自由度；在边界附近的协方差近似尤其脆弱。

## 9. 与 RamanSPy 的关系

RamanSPy 负责统一 Raman 光谱容器、预处理、降维和解混；lmfit 负责给定正向函数后的参数估计与不确定度。典型连接方式是：从 RamanSPy 取出 `spectral_axis` 与一条预处理谱，把它们传给 lmfit 的 `Model.fit`，并将峰面积/中心/宽度作为后续空间映射的参数。两者的模型假设必须一致：例如 RamanSPy 的基线校正会改变 lmfit 所见的残差和峰面积，因此预处理步骤应固定并记录。

## 10. 源码依据

- `lmfit/minimizer.py`：残差约化、支持的优化器、统计量、协方差与边界变换。
- `lmfit/parameter.py`：命名参数、边界、`vary` 和表达式约束。
- `lmfit/model.py`：`Model`、复合模型、加权/复数残差和拟合接口。
- `lmfit/models.py`、`lmfit/lineshapes.py`：内置峰形与参数关系。
- 官方文档 `doc/intro.rst`、`doc/fitting.rst`、`doc/model.rst`、`doc/builtin_models.rst`、`doc/confidence.rst`：统计解释与使用边界。
