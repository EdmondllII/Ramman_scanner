# RamanSPy：数学与物理原理调研

## 0. 调研范围

本文依据工作区中的 `RamanSPy`（`pyproject.toml` 标示版本 0.2.10）源码、内置文档和示例整理。重点是它隐含的信号模型与数学算法，而不是 API 说明。RamanSPy 本身是光谱数据分析框架，并不求解电磁场或量子散射的正向问题。

## 1. 拉曼测量的物理抽象

### 1.1 Raman shift 轴

实验器件通常给出波长 `lambda`，而材料振动信息用波数位移表示。若激光波长为 `lambda_0`（nm），源码中的变换为

\[
\Delta \tilde{\nu} = \frac{10^7}{\lambda_0} - \frac{10^7}{\lambda}
\quad (\mathrm{cm}^{-1})
\]

这对应 Stokes 位移的频率差。RamanSPy 统一要求最后一维是按该位移排序的光谱轴，因此不同空间位置的光谱才能逐点比较、堆叠和做矩阵分解。

### 1.2 信号分解

对一个采样点，包中的处理可以抽象为

\[
y(\nu) = s(\nu) + b(\nu) + c(\nu) + \varepsilon(\nu)
\]

其中 `s` 是与分子振动相关的 Raman 峰，`b` 是荧光/仪器背景，`c` 是宇宙射线等稀疏异常，`eps` 是随机噪声。这个分解是工程上的可加性假设：RamanSPy 的基线校正、去尖峰和去噪分别估计并移除后三项。

从微观上说，Raman 峰来自入射光诱导的极化率变化；峰强受极化率导数、偏振和占据数影响。RamanSPy 不使用这些量子/电磁参数，而把每个峰当作观测向量中的结构化信号。

## 2. 数据结构：光谱张量与线性代数对象

`SpectralContainer` 将数据存为 `(..., B)`，最后的 `B` 是波数采样，前面的轴是像素、切片或体素。分析时先把空间轴展平为矩阵

\[
X \in \mathbb{R}^{N \times B},
\qquad N = \text{像素/光谱条数}.
\]

处理后再折叠回原空间形状。这使 PCA、NMF、聚类和解混共享同一个矩阵接口。合并多个对象前要求波数轴逐点一致；源码中的 `is_aligned` 只检查轴值相同，不会自动插值。

## 3. 预处理中的核心数学

### 3.1 Whittaker 平滑与基线校正

离散二阶差分矩阵记为 `D`。Whittaker 平滑求解

\[
\min_z \; \lVert y-z \rVert_2^2 + \lambda \lVert D^d z \rVert_2^2
\]

其正规方程为 $(I + \lambda D^T D) z = y$。`lambda` 越大，越强制基线/信号平滑。

AsLS 及其 airPLS、arPLS、asPLS 等变体把第一项改成带权形式

\[
\min_z \; (y-z)^\mathsf{T} W (y-z) + \lambda \lVert D^d z \rVert_2^2
\]

并迭代更新 `W`：低于候选基线的点获得较大权重，高于基线的峰获得较小权重。物理意图是“荧光背景应平滑，窄 Raman 峰不应被基线吸收”。这些算法由 `pybaselines` 实现，RamanSPy 负责沿最后一轴广播并做 `y-z`。

多项式基线则在指定波数区间上拟合

\[
b(\nu) = \sum_{j=0}^{p} c_j \nu^j
\]

再从光谱中减去。它的解释性强，但对宽峰和高阶基线容易混淆。

### 3.2 去噪

- Savitzky--Golay：每个滑动窗口内用低阶多项式最小二乘拟合，并取中心值；因此在合适窗口下比简单移动平均更能保留峰位置和低阶形状。
- Gaussian：对光谱做高斯核卷积，频域上相当于抑制高频噪声；`sigma` 决定分辨率损失。
- Whittaker：上面的二次惩罚平滑，同一框架既可去噪也可估计基线。

### 3.3 宇宙射线去除

Whitaker--Hayes 方法对一阶差分 `Delta y_i = y_(i+1)-y_i` 计算

\[
z_i = 0.6745\,
\frac{\Delta y_i - \operatorname{median}(\Delta y)}
{\operatorname{MAD}(\Delta y)}
\]

绝对值超过阈值的点被视为尖峰，并用邻域内非尖峰均值替换，迭代至没有异常点。这里利用了宇宙射线“窄、稀疏、差分幅度大”的统计特征；它不是对 Raman 峰的物理判别，宽而真实的峰可能不会被检测。

### 3.4 归一化

Raman 强度常受激光功率、积分时间、聚焦和样品量影响。包中提供的变换是尺度处理，不是物理定量校准：

\[
\begin{aligned}
\text{Vector}:&\quad \frac{x}{\lVert x \rVert_2}, \\
\text{MaxIntensity}:&\quad \frac{x}{\max(x)}, \\
\text{Min--Max}:&\quad a+\frac{(x-\min(x))(b-a)}{\max(x)-\min(x)}, \\
\text{AUC}:&\quad \frac{x}{\int x(\nu)\,\mathrm{d}\nu}.
\end{aligned}
\]

默认按像素逐条计算；关闭 `pixelwise` 时使用整个容器的参考尺度。AUC 使用梯形积分，所以不均匀波数采样会直接改变归一化结果。

## 4. 降维与聚类

### 4.1 PCA

对中心化矩阵 `X_c` 做 SVD：`X_c = U Sigma V^T`。谱形主成分是 `V` 的行，像素得分是 `U Sigma`。等价地，前 `k` 个方向最大化投影方差，或最小化秩 `k` 的 Frobenius 重构误差

\[
\min_{\operatorname{rank}(\widehat{X}) \leq k}
\lVert X_c-\widehat{X}\rVert_F^2
\]

PCA 允许正负系数，因此主成分是统计基，不必对应真实化学组分。

### 4.2 NMF 与 ICA

NMF 求非负因子

\[
X \approx WH,
\qquad W \geq 0,\quad H \geq 0
\]

通常最小化 `||X-WH||_F^2`（具体求解由 scikit-learn 完成）。非负性与“光谱强度、组分丰度非负”的物理直觉一致，但分解仍有尺度和旋转不唯一性。

ICA 设观测谱是独立潜变量的线性混合 `X = A S`，通过最大化非高斯性/最小化互信息估计独立源。独立性并不等同于化学纯度，因此 ICA 结果应视为统计分离。

### 4.3 K-means

对像素光谱求解

\[
\min_{\{\ell_i\},\{\mu_k\}}
\sum_i \lVert x_i-\mu_{\ell_i}\rVert_2^2
\]

欧氏距离意味着每个波数点等权，且簇近似球状。源码将标签转成 one-hot 图，把质心作为代表谱；这不是端元丰度估计。

## 5. 光谱解混的物理与几何

### 5.1 线性混合模型

设 `K` 个端元谱组成矩阵 `S`，像素 `p` 的观测为

\[
y_p = S^\mathsf{T}a_p + \varepsilon_p
\]

其中丰度向量通常满足 `a_p >= 0`，并可满足和为 1（FCLS）。这是“光斑内不同成分贡献的 Raman 强度可加”的近似；它忽略多重散射、化学增强、折射率变化和组分间相互作用。

UCLS 只解最小二乘，NNLS 加非负约束，FCLS 同时加非负和和为 1 的约束。端元提取器包括：

- PPI/FIPPI：在随机投影下寻找极端像素；
- N-FINDR：寻找使端元单纯形体积最大的像素集合；
- VCA：先按 SVD 投影到低维子空间，再沿随机方向寻找凸包顶点。

这些方法都隐含“纯像素/凸包”假设：观测谱位于端元凸包（或其近似）内。没有纯像素、端元数设错或基线残留时，几何端元可能只是数学顶点而非纯物质谱。

### 5.2 合成数据中的双线性模型

`synth.mix` 还实现

\[
y_p = \sum_k a_{pk}s_k
    + \sum_{k<l} a_{pk}a_{pl}(s_k \odot s_l)
    + \text{noise} + \text{baseline} + \text{cosmic\_spikes}
\]

其中 `o` 是逐波数乘积。它用于模拟组分交互导致的非线性，但不是 Raman 辐射传输方程；因此适合算法测试，不应直接当作实验机理。

## 6. 结论与使用边界

RamanSPy 的核心思想是：先把实验光谱映射为统一坐标下的高维向量，再用平滑/稀疏异常模型清理观测，最后用线性代数和凸几何完成表征。其数学方法成熟且可组合，但物理约束大多是弱约束（非负、平滑、可加），并未编码偏振选择定则、峰的量子振动归属或仪器响应函数。定量解释时应额外建立峰形/响应/噪声的正向模型，并验证预处理没有改变目标峰的面积、位置和宽度。

## 7. 源码依据

- `RamanSPy/src/ramanspy/core.py`：容器、展平/折叠和峰检测。
- `RamanSPy/src/ramanspy/preprocessing/denoise.py`、`baseline.py`、`despike.py`、`normalise.py`：上述预处理公式的调用与广播。
- `RamanSPy/src/ramanspy/analysis/decompose.py`、`cluster.py`、`unmix.py`：PCA/NMF/ICA、K-means 和端元/丰度流程。
- `RamanSPy/src/ramanspy/synth/synth.py`：高斯峰、线性/双线性混合及噪声模拟。
