# pybaselines：数学与物理原理调研

## 0. 调研范围

本文依据工作区中的 `pybaselines` 源码、README、算法文档和测试用例整理。当前源码版本元数据为 1.2.1。重点讨论基线校正的数学结构、物理假设和数值实现，不逐一罗列全部 API。

## 1. 基线校正的物理问题

### 1.1 观测模型

对 Raman、FTIR、NMR、XRD 等实验数据，pybaselines 将观测抽象为

\[
y(x)=s(x)+b(x)+\varepsilon(x),
\]

其中 \(s\) 是希望保留的窄峰/结构，\(b\) 是缓慢变化的背景（例如荧光、自发光、散射或仪器漂移），\(\varepsilon\) 是噪声。算法输出基线 \(\widehat b\)，通常由

\[
\widehat s(x)=y(x)-\widehat b(x)
\]

得到校正信号。

这里的“基线”不是由某个统一的微观物理定律定义的，而是一个尺度假设：相对于目标峰，背景变化更慢、更平滑，或者可以由低复杂度函数表示。因此基线校正本质上是带先验的信号分离问题。

### 1.2 统一 API 与数值对象

一维 `Baseline` 以 \(y\in\mathbb{R}^{N}\) 为输入，二维 `Baseline2D` 处理矩阵 \(Y\in\mathbb{R}^{M\times N}\)；算法通常返回基线和包含权重、收敛历史、系数等信息的字典。`x_data` 只用于构造实际坐标，很多窗口参数仍按采样点索引计数，而不是按物理单位计数。

源码会对未排序的自变量进行排序、计算，再恢复原顺序；这避免了插值和差分算法把非单调坐标误当作均匀坐标。但非均匀采样仍会影响差分、窗口和多项式尺度，使用时应检查坐标间距。

## 2. Whittaker 平滑：整个库的主干

### 2.1 惩罚最小二乘

令 \(v\) 为待估计基线，\(D_d\) 为 \(d\) 阶有限差分矩阵，\(W=\operatorname{diag}(w_i)\) 为数据权重。pybaselines 的核心问题是

\[
\min_{v}\;
(y-v)^\mathsf{T}W(y-v)
+\lambda\lVert D_dv\rVert_2^2.
\]

第一项让基线贴近观测，第二项惩罚曲率或更高阶差分。\(\lambda\) 越大，基线越平滑；\(d=2\) 时惩罚离散二阶导数，常用于允许线性趋势但抑制弯曲。

令目标函数对 \(v\) 的梯度为零，得到带状线性系统

\[
\bigl(W+\lambda D_d^\mathsf{T}D_d\bigr)v=Wy.
\]

`utils.whittaker_smooth` 和 `whittaker.py` 复用稀疏/带状系统求解器，而不是显式求逆。矩阵的带状结构是算法能处理长光谱的关键。

### 2.2 AsLS 与迭代重加权

普通平滑会被高于基线的 Raman 峰拉高。AsLS 通过迭代更新权重，让“峰上方”的点对基线拟合贡献较小：

\[
w_i=
\begin{cases}
p, & y_i>v_i,\\
1-p, & y_i\le v_i.
\end{cases}
\]

每轮依次执行“解线性系统 -> 根据残差更新权重”，直到权重或基线的相对变化小于 `tol`。\(p\) 很小时，算法倾向寻找位于信号下方的平滑曲线；\(p\) 接近 0.5 时，正负残差更对称。

airPLS、arPLS、IARPLS、DRPLS、asPLS、PSALSA 等方法都保留上述线性系统，区别主要在权重函数：有的根据负残差的统计分布自适应，有的对正残差使用指数衰减，有的让平滑参数随位置变化。它们不是完全不同的优化框架，而是不同的鲁棒估计/峰屏蔽策略。

例如，若把残差 \(r_i=y_i-v_i\) 看成“噪声点 + 峰点”的混合，权重可以理解为该点属于背景噪声的可信度。于是迭代重加权近似求解一个非二次、非对称的鲁棒损失问题。

### 2.3 参数尺度

\(\lambda\) 依赖采样点数。数据点数增加时，差分惩罚与残差项的相对尺度改变，保持相似平滑效果通常需要增大 \(\lambda\)。因此不能把一个数据长度上的经验值机械复制到另一种采样密度或截取区间。

## 3. 多项式基线与鲁棒拟合

### 3.1 普通多项式

基线写成

\[
p(x)=\sum_{j=0}^{m}\beta_jx^j.
\]

加权最小二乘为

\[
\min_{\beta}\;\sum_{i=1}^{N}w_i^2\bigl(y_i-p(x_i)\bigr)^2.
\]

源码使用 Vandermonde 矩阵和伪逆求系数，并会把 \(x\) 线性缩放到适合数值计算的域。若已知无峰区间，可把峰区权重设为 0，这相当于选择性掩膜。

### 3.2 ModPoly、IModPoly 与惩罚损失

ModPoly 不手工指定峰区，而是先做一次多项式拟合，再把下一轮拟合用的数据替换为逐点最小值：

\[
y_i^{(k+1)}=\min\!\bigl(y_i^{(k)},p^{(k)}(x_i)\bigr).
\]

这样高于当前基线的峰会被截掉，低于基线的点保留。IModPoly 进一步用残差标准差设置阈值，并可自动屏蔽初始峰。

`penalized_poly` 则在多项式模型上使用截断二次、Huber 或其他非二次代价。其思想与 M-estimation 相同：小残差保持二次损失以获得高效局部拟合，大残差降低影响以抑制峰和离群点。

多项式方法的优点是参数少、解释直接；缺点是高阶多项式容易振荡，低阶多项式又可能无法表示明显弯曲或指数型荧光背景。

## 4. Penalized splines：局部灵活性与全局平滑

### 4.1 B-spline 表示

基线用 B-spline 基函数表示：

\[
v(x_i)=\sum_{j=1}^{M}B_j(x_i)c_j.
\]

P-spline 在拟合项之外惩罚系数的差分：

\[
\min_{c}\;
\sum_{i=1}^{N}w_i\left(y_i-\sum_{j=1}^{M}B_j(x_i)c_j\right)^2
+\lambda\lVert D_dc\rVert_2^2.
\]

对应线性系统为

\[
\bigl(B^\mathsf{T}WB+\lambda D_d^\mathsf{T}D_d\bigr)c
=B^\mathsf{T}Wy.
\]

相比直接对每个数据点做 Whittaker 平滑，P-spline 用较少的基函数压缩自由度；相比低阶多项式，它能局部改变形状。pybaselines 提供 `pspline_asls`、`pspline_airpls` 等，把 Whittaker 的权重更新机制移植到 B-spline 系数空间。

### 4.2 概率/分位数观点

`mixture_model` 把残差视为背景噪声与峰的混合：通常用以 0 为中心的正态分布表示噪声，用均匀分布表示正残差峰，依据后验概率更新 P-spline 权重。

`irsqr` 使用分位数回归。分位数 \(q\) 的非对称绝对损失为

\[
\rho_q(r)=
\begin{cases}
q\,r, & r\ge 0,\\
(q-1)\,r, & r<0.
\end{cases}
\]

代码通过 IRLS 用平滑权重近似该损失。较小的 \(q\) 偏向拟合数据分布的下分位曲线，因此适合把正峰看作偏离背景的成分。

## 5. 形态学基线：不依赖显式函数族

数学形态学在移动窗口内使用最大值和最小值。对结构元素 \(K\)，灰度膨胀和腐蚀可写为

\[
(y\oplus K)(i)=\max_{k\in K}y(i-k),
\qquad
(y\ominus K)(i)=\min_{k\in K}y(i+k).
\]

开运算和闭运算分别是

\[
y\circ K=(y\ominus K)\oplus K,
\qquad
y\bullet K=(y\oplus K)\ominus K.
\]

当窗口比峰宽更大时，开运算会去掉窄的正峰而保留慢变化背景；`mor`、`rolling_ball`、`mormol`、`amormol` 等方法在此基础上增加平均、卷积或迭代。`mpls` 先用形态学开运算寻找基线锚点，再把锚点赋予较大权重，交给 Whittaker 系统平滑。

形态学方法的关键参数是 `half_window`，它按索引而非 \(x\) 的物理单位定义。窗口过小会把峰误当背景，过大则会抹掉真实的宽背景结构；某些算法支持 `optimize_window`，通过连续窗口下开运算结果的相对变化选择稳定窗口。

## 6. 平滑与峰裁剪方法

### 6.1 SNIP

SNIP（Statistics-sensitive Non-linear Iterative Peak-clipping）在半窗口 \(k\) 下用两端平均值构造候选值，并逐点取最小值：

\[
y_i^{(k+1)}=\min\!\left(y_i^{(k)},
\frac{y_{i-k}^{(k)}+y_{i+k}^{(k)}}{2}\right).
\]

逐渐增大窗口会逐步削除窄峰；反向窗口序列通常得到更平滑的结果。最大窗口应接近最大峰宽的一半，否则会把宽峰或宽背景一并裁掉。

### 6.2 移动统计量

`noise_median` 用滑动窗口中位数估计背景，再用高斯核平滑；`swima` 迭代移动平均并逐点取最小值；`ipsa` 重复 Savitzky--Golay 平滑。这类方法依赖“峰在窗口内占少数”的统计假设，密集峰、重叠峰或峰宽接近窗口时会失效。

## 7. 分类、优化器与稀疏模型

### 7.1 分类型方法

`dietrich`、`golotvin`、`std_distribution`、`fastchrom` 等先根据局部导数、滚动极差或滚动标准差把采样点分成“可能是基线”和“可能是峰”两类，再对基线点插值或拟合。它们把基线识别转化为分类问题，而不是直接优化单个全局损失。

例如，若局部标准差 \(s_i\) 小于噪声尺度阈值，则认为该窗口主要包含背景；这一规则隐含峰使局部波动变大的假设。分类错误会通过后续插值直接传播到基线。

### 7.2 优化器包装

`optimize_extended_range` 在数据左右边缘外推线性基线并添加合成 Gaussian 峰，然后对扩展数据运行指定的 Whittaker、多项式或样条算法，最后裁回原区间。它主要缓解边界效应：有限窗口和差分惩罚在端点处约束较弱，人工延拓给端点增加了几何上下文。

### 7.3 BEADS：频域低通与稀疏先验

`beads` 把基线看成低通成分，把信号及其导数视为稀疏成分。抽象地可写成

\[
y=b+s+\varepsilon,
\]

并最小化包含低通平滑惩罚和稀疏惩罚的目标：

\[
\min_{b,s}
\frac12\lVert y-b-s\rVert_2^2
+\lambda_0\,\Phi_0(s)
+\lambda_1\,\Phi_1(Ds)
+\lambda_2\,\Phi_2(D^2s),
\]

其中 \(\Phi\) 是促进稀疏性的非二次代价，`freq_cutoff` 控制基线低通范围。该模型更接近“峰是局部稀疏结构、背景是低频结构”的信号处理观点，但参数解释依赖采样率和频谱形状。

## 8. 二维推广

二维算法处理 \(Y\in\mathbb{R}^{M\times N}\)，分别沿行和列惩罚差分。展平后，二维 Whittaker 目标可写成

\[
\min_{v}\;
\lVert W^{1/2}(y-v)\rVert_2^2
+\lambda_r\lVert D_r v\rVert_2^2
+\lambda_c\lVert D_c v\rVert_2^2.
\]

其线性系统具有 Kronecker 和结构：

\[
\left(
W_{\mathrm{diag}}
+\lambda_r(I_N\otimes D_r^\mathsf{T}D_r)
+\lambda_c(D_c^\mathsf{T}D_c\otimes I_M)
\right)v
=W_{\mathrm{diag}}y.
\]

二维 P-spline 则把 \(v\) 换成张量积 B-spline 表示。直接构造 \(MN\times MN\) 矩阵代价很高，因此源码提供稀疏求解、广义线性阵列模型以及基于惩罚矩阵特征分解的降维实现。行列的 \(\lambda\) 可以不同，适合各向异性的空间背景。

## 9. 数值实现与诊断

1. **稀疏/带状线性代数**：差分惩罚产生带状矩阵，P-spline 产生稀疏设计矩阵；求解器支持 SciPy 稀疏格式，并可选用 `pentapy`、`numba` 等加速。
2. **收敛判据**：多数迭代算法记录 `tol_history`，以基线、权重或残差的相对变化作为停止条件；达到 `max_iter` 仍未满足 `tol` 时，结果不应被视为已收敛。
3. **边界与填充**：库提供镜像、线性外推等 padding 选项。边界条件会显著影响端点基线，尤其是短光谱或强弯曲背景。
4. **权重和掩膜**：自定义权重是最直接的物理先验接口，可以把已知峰区设为 0，或根据实验误差设置不同可信度。
5. **输入尺度**：差分矩阵、窗口和多项式 Vandermonde 矩阵都受横轴尺度影响。使用真实 `x_data`、统一单位并避免极端坐标范围有助于稳定性。

## 10. 物理解释的边界

pybaselines 的“基线”主要是平滑/低复杂度的数学对象，不等于某个唯一的荧光或散射正向模型。不同算法可能在同一数据上给出不同 \(\widehat b\)，而且没有仅凭残差就能判断哪条基线具有真实物理意义。

对 Raman 定量而言，基线错误会系统性改变峰面积、峰高和低频宽峰。应将算法选择、\(\lambda\)、窗口、权重、收敛状态和横轴单位作为结果的一部分记录。若目标是温度、应力、浓度或峰位的物理反演，最好把背景函数、仪器响应和噪声统计一起放进显式正向模型，而不是把基线校正当作完全无偏的预处理。

## 11. 与 RamanSPy、lmfit 的关系

RamanSPy 在其预处理模块中调用 `pybaselines` 的 ASLS、airPLS、arPLS、DRPLS、ASPLS 等函数，沿每条光谱广播并执行 \(y-\widehat b\)。因此 RamanSPy 提供数据容器和流程编排，pybaselines 提供基线估计。

若随后用 lmfit 拟合峰形，lmfit 看到的是扣除 \(\widehat b\) 后的信号。基线估计误差会进入峰参数误差，但通常不会自动传递到 lmfit 的协方差矩阵；需要联合拟合或 bootstrap 才能反映这部分不确定度。

## 12. 源码依据

- `pybaselines/pybaselines/whittaker.py`、`utils.py`：Whittaker 线性系统、差分矩阵和迭代重加权。
- `pybaselines/pybaselines/polynomial.py`：多项式、ModPoly、IModPoly 与非二次损失。
- `pybaselines/pybaselines/spline.py`、`_spline_utils.py`：B-spline、P-spline、混合模型与分位数回归。
- `pybaselines/pybaselines/morphological.py`：形态学开闭运算、rolling-ball 和 mPLS。
- `pybaselines/pybaselines/smooth.py`、`classification.py`、`optimizers.py`、`misc.py`：SNIP、移动平滑、分类算法、扩展范围和 BEADS。
- `pybaselines/two_d/`：二维 Whittaker、样条、多项式和形态学方法。
