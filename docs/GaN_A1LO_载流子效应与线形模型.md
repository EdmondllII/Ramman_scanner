# GaN A1(LO) 载流子效应专题：LOPC 与 Raman Fano 干涉

## 0. 阅读方式与范围

本文只把下面两种机制作为正文的主线：

1. **LO 声子-等离激元耦合（LOPC）**：载流子集体振荡与极性 LO 声子通过纵向电场耦合，改变系统的本征模。数学上首先是复介电函数 \(\epsilon(\omega)\) 的零点（或相应响应函数的极点）问题。
2. **载流子引起的 Raman Fano 干涉**：离散声子散射振幅与电子连续态散射振幅相干叠加。数学上必须先相加复振幅，再取模平方。

角向色散、普通声子自能、空间不均匀性和仪器展宽也可能改变峰形，但它们不是本文的同等主线，统一放在文末附录，主要用于排除误判。

为便于推导，全文默认：

- \(\omega\) 表示角频率，时间因子采用 \(\exp(-i\omega t)\)；
- Raman 横轴若使用波数 \(\widetilde\nu\)（\(\mathrm{cm^{-1}}\)），最后再用 \(\omega=2\pi c\widetilde\nu\) 转换；
- “峰位”指响应函数的峰位置，不自动等同于介电函数零点的实部；阻尼和仪器卷积会使二者不同；
- 当前项目若固定使用 airPLS，应把基线方法和参数固定记录。基线扣除是数据预处理，不应被复杂峰形模型用来吸收真实的电子连续背景。

对数学读者，最重要的区别可以先写成：

\[
\text{LOPC:}\quad \epsilon(\omega; n,\mu,\ldots)=0,
\qquad
\text{Fano:}\quad I(\omega)\propto
\left\lvert f_{\mathrm{cont}}(\omega)+f_{\mathrm{ph}}(\omega)\right\rvert^2.
\]

前者改变的是耦合系统的谱结构，后者改变的是两条散射路径之间的交叉项。

## 1. 共同的谱学起点

### 1.1 为什么 A1(LO) 能感受到载流子

纤锌矿 GaN 的 \(A_1(\mathrm{LO})\) 是极性纵光学声子。Ga、N 子晶格沿纵向相对位移会产生宏观纵向电场，因此该声子与自由载流子的纵向电荷密度振荡具有相同的电场通道。载流子可能通过三种层次进入观测谱：

- 形成等离激元，与 LO 声子形成 LOPC 集体模；
- 通过电子-声子自能改变本征峰位和线宽；
- 形成电子 Raman 连续态，与离散声子散射振幅发生 Fano 干涉。

本文正文只展开 LOPC 和 Fano；自能作为附录的较弱或间接效应讨论。

GaN 中 \(A_1(\mathrm{LO})\)-plasmon 耦合已在不同电子浓度的 n-GaN 中直接观测，并用于拟合载流子浓度和阻尼；早期结果还与 Hall 测量进行了比较。[Kozawa 等（1994）](https://doi.org/10.1063/1.356492) [Demangeot 等（1997）](https://doi.org/10.1063/1.365903)

### 1.2 观测模型和参考线形

任何具体机制最终都要经过仪器和空间采样。用 \(S(\omega)\) 表示样品本征 Raman 响应，一个通用观测式是：

\[
I_{\mathrm{obs}}(\omega)
=\left[S(\omega)*h_{\mathrm{inst}}(\omega)\right]
+B(\omega)+\varepsilon(\omega),
\]

卷积定义为：

\[
(f*g)(\omega)=
\int_{-\infty}^{\infty}f(\omega')g(\omega-\omega')\,\mathrm d\omega'.
\]

其中 \(h_{\mathrm{inst}}\) 是仪器线扩散函数，\(B\) 是背景，\(\varepsilon\) 是测量噪声。若仪器函数近似为 Gaussian：

\[
G(\omega;\sigma)=
\frac{1}{\sqrt{2\pi}\sigma}
\exp\left(-\frac{\omega^2}{2\sigma^2}\right),
\]

则卷积作用于完整的样品响应：

\[
I_{\mathrm{obs}}(\omega)-B(\omega)
=
\int S(\omega')G(\omega-\omega';\sigma_{\mathrm{inst}})
\,\mathrm d\omega'
+\varepsilon(\omega).
\]

在没有明显载流子耦合、电子连续态和角向色散时，可把参考声子近似成 Lorentzian，并与 Gaussian 展宽卷积：

\[
I_{\mathrm{V}}(\omega)
=A\,[G(\omega;\sigma)*L(\omega;\omega_0,\gamma_{\mathrm{ph}})].
\]

其中：

\[
L(\omega;\omega_0,\gamma_{\mathrm{ph}})
=
\frac{1}{\pi}
\frac{\gamma_{\mathrm{ph}}}
{(\omega-\omega_0)^2+\gamma_{\mathrm{ph}}^2},
\qquad
\gamma_{\mathrm{ph}}=\mathrm{HWHM}.
\]

Voigt 只作为参考模型；若峰位、宽度或强度随自由载流子显著变化，应检验 LOPC 或 Fano，而不是只增大 Voigt 宽度。

非极性的 \(E_2(\mathrm{high})\) 模没有同样的宏观纵向电场，通常可作为应变和晶格温度的对照峰，但这不意味着它完全不受载流子影响。

## 2. 主线一：LO 声子-等离激元耦合（LOPC）

### 2.1 耦合的物理和数学对象

自由载流子形成等离激元，极性 LO 声子形成带宏观电场的晶格集体模。两者不是“两个峰恰好靠得很近”，而是通过纵向电场耦合后产生新的本征解，通常记作 \(L^+\) 和 \(L^-\)。

因此 LOPC 的基本问题不是把两个独立 Voigt 相加，而是求耦合介质的纵向响应。更一般地，纵向电磁场满足 \(\mathbf q\cdot\mathbf D=0\)，在各向异性介质中相应条件是：

\[
\mathbf q^{\mathsf T}\boldsymbol\epsilon(\mathbf q,\omega)\mathbf q=0.
\]

本文采用标量介电函数，是对选定晶向、长波极限（\(q\simeq0\)）的最小近似；此时纵向模条件简化为：

\[
\epsilon(\omega)=0.
\]

有阻尼时零点位于复频率平面；实验上看到的峰是相应 Raman 响应经过阻尼、散射矩阵元和仪器卷积后的结果。

### 2.2 复介电函数的构造

先从两个线性响应方程开始。取 \(Q\) 为归一化的极性晶格坐标，\(P_{\mathrm c}\) 为载流子极化：

\[
\ddot Q+\gamma_{\mathrm{ph}}\dot Q+\omega_{\mathrm{TO}}^2Q=gE,
\]

\[
\ddot P_{\mathrm c}+\gamma_p\dot P_{\mathrm c}
=\epsilon_0\epsilon_\infty\omega_p^2E.
\]

取 \(P_{\mathrm{ph}}=gQ\)，并用归一化条件：

\[
g^2=\epsilon_0\epsilon_\infty
(\omega_{\mathrm{LO}}^2-\omega_{\mathrm{TO}}^2).
\]

在 \(\exp(-i\omega t)\) 约定下：

\[
P_{\mathrm{ph}}=
\epsilon_0\epsilon_\infty
\frac{\omega_{\mathrm{LO}}^2-\omega_{\mathrm{TO}}^2}
{\omega_{\mathrm{TO}}^2-\omega^2-i\gamma_{\mathrm{ph}}\omega}E,
\]

\[
P_{\mathrm c}=
-\epsilon_0\epsilon_\infty
\frac{\omega_p^2}
{\omega^2+i\gamma_p\omega}E.
\]

由

\[
D=\epsilon_0\epsilon_\infty E+P_{\mathrm{ph}}+P_{\mathrm c},
\qquad
D=\epsilon_0\epsilon(\omega)E,
\]

得到极性晶格振子的介电函数：

\[
\epsilon_{\mathrm{lat}}(\omega)
=\epsilon_\infty
\left[
1+
\frac{\omega_{\mathrm{LO}}^2-\omega_{\mathrm{TO}}^2}
{\omega_{\mathrm{TO}}^2-\omega^2-i\gamma_{\mathrm{ph}}\omega}
\right].
\]

加入自由载流子的 Drude 响应后，得到最小标量模型：

\[
\epsilon(\omega)=\epsilon_\infty
\left[
1+
\frac{\omega_{\mathrm{LO}}^2-\omega_{\mathrm{TO}}^2}
{\omega_{\mathrm{TO}}^2-\omega^2-i\gamma_{\mathrm{ph}}\omega}
-
\frac{\omega_p^2}
{\omega^2+i\gamma_p\omega}
\right].
\]

令

\[
\Delta_{\mathrm{LO}}=\omega_{\mathrm{LO}}^2-\omega_{\mathrm{TO}}^2,
\qquad
D_{\mathrm{ph}}(\omega)=
(\omega_{\mathrm{TO}}^2-\omega^2)^2
+\gamma_{\mathrm{ph}}^2\omega^2,
\]

则在 \(\omega>0\) 时：

\[
\frac{\epsilon'(\omega)}{\epsilon_\infty}
=1+\Delta_{\mathrm{LO}}
\frac{\omega_{\mathrm{TO}}^2-\omega^2}{D_{\mathrm{ph}}(\omega)}
-\frac{\omega_p^2}{\omega^2+\gamma_p^2},
\]

\[
\frac{\epsilon''(\omega)}{\epsilon_\infty}
=\Delta_{\mathrm{LO}}
\frac{\gamma_{\mathrm{ph}}\omega}{D_{\mathrm{ph}}(\omega)}
+\frac{\omega_p^2\gamma_p}
{\omega(\omega^2+\gamma_p^2)}.
\]

因此：

\[
\operatorname{Im}\left[-\frac1{\epsilon}\right]
=
\frac{\epsilon''}{(\epsilon')^2+(\epsilon'')^2}.
\]

各项的含义是：

- \(\epsilon_\infty\)：高频介电常数，表示不在此频段显式建模的电子极化；
- \(\omega_{\mathrm{TO}}\)、\(\omega_{\mathrm{LO}}\)：无自由载流子时的横向和纵向光学声子频率；
- \(\gamma_{\mathrm{ph}}\)：声子阻尼；
- \(\omega_p\)：已经除以 \(\epsilon_\infty\) 的屏蔽等离子频率；
- \(\gamma_p=1/\tau\)：载流子动量弛豫率。

在 SI 单位下：

\[
\omega_p^2=
\frac{n e^2}{\epsilon_0\epsilon_\infty m^*},
\qquad
\gamma_p=\frac{1}{\tau}=
\frac{e}{m^*\mu}.
\]

\[
[n]=\mathrm{m^{-3}},
\qquad
[\omega_p]=[\gamma_p]=\mathrm{s^{-1}},
\qquad
[\mu]=\mathrm{m^2\,V^{-1}\,s^{-1}}.
\]

不同文献有时把未除以 \(\epsilon_\infty\) 的量称为裸等离子频率。实现时必须检查定义，不能只看符号 \(\omega_p\)。若采用 \(\exp(+i\omega t)\)，介电函数虚部的符号会整体改变，但物理吸收和最终强度不变；代码中应统一时间约定。

### 2.3 特征方程与无阻尼极限

保留阻尼时，\(\epsilon(\omega)=0\) 等价于复频率特征方程：

\[
\left(\omega^2+i\gamma_p\omega\right)
\left(\omega_{\mathrm{LO}}^2-\omega^2-i\gamma_{\mathrm{ph}}\omega\right)
-\omega_p^2
\left(\omega_{\mathrm{TO}}^2-\omega^2-i\gamma_{\mathrm{ph}}\omega\right)
=0.
\]

其复根同时给出耦合模的振荡频率和衰减率。无阻尼时令
\(\gamma_{\mathrm{ph}}=\gamma_p=0\)、\(x=\omega^2\)，得到实系数二次方程：

\[
x^2-(\omega_{\mathrm{LO}}^2+\omega_p^2)x
+\omega_p^2\omega_{\mathrm{TO}}^2=0.
\]

所以两个纵向耦合模为：

\[
\omega_{\pm}^2=
\frac{1}{2}
\left[
\omega_{\mathrm{LO}}^2+\omega_p^2
\pm
\sqrt{(\omega_{\mathrm{LO}}^2+\omega_p^2)^2
-4\omega_p^2\omega_{\mathrm{TO}}^2}
\right].
\]

极限检查和低浓度展开为：

\[
\omega_p\to0:
\qquad
\omega_+\to\omega_{\mathrm{LO}},
\qquad
\omega_-\to0.
\]

\[
\omega_p^2\ll\omega_{\mathrm{LO}}^2:
\qquad
\omega_+^2\simeq
\omega_{\mathrm{LO}}^2
+\omega_p^2
\left(
1-\frac{\omega_{\mathrm{TO}}^2}
{\omega_{\mathrm{LO}}^2}
\right),
\]

\[
\omega_-^2\simeq
\omega_p^2
\frac{\omega_{\mathrm{TO}}^2}
{\omega_{\mathrm{LO}}^2}.
\]

\[
\omega_p^2\propto n,
\qquad
\omega_\pm\neq a+bn
\quad\text{（一般情形）}.
\]

载流子增加时，\(L^+\) 通常更 plasmon-like；当 \(\gamma_p\) 很大时，plasmon 过阻尼，两个分支可能无法分辨。

Kozawa 等在不同载流子浓度的 n-GaN 中观察到 LO 带向高频移动并展宽，并以过阻尼等离激元与 LO 声子耦合解释。[Kozawa 等（1994）](https://doi.org/10.1063/1.356492) Wieser 等也对 GaN 层中的 LO 声子-等离激元耦合进行了 Raman 研究。[Wieser 等（1998）](https://doi.org/10.1016/S0022-0248(98)00242-5) Demangeot 等进一步对 \(q=0\) 的 \(A_1(\mathrm{LO})\)-plasmon 线形进行介电模型计算，并讨论了空间电子浓度不均匀和有限 \(q\) 屏蔽。[Demangeot 等（1997）](https://doi.org/10.1063/1.365903)

### 2.4 LOPC 的 Raman 线形

忽略复杂 Raman 张量细节时，可以把最小样品响应写成介电损耗函数：

\[
S_{\mathrm{LOPC}}(\omega)=
A\,[n_B(\omega,T)+1]
R(\omega)
\operatorname{Im}\left[-\frac{1}{\epsilon(\omega)}\right].
\]

其中：

\[
n_B(\omega,T)=
\frac{1}{\exp(\hbar\omega/k_B T)-1}
\]

是 Stokes 散射的 Bose 因子，\(R(\omega)\) 代表 Raman 散射矩阵元、偏振几何以及形变势和电光散射贡献。Kozawa 等指出，形变势和电光机制会影响 GaN 耦合模 Raman 强度，因此 \(\operatorname{Im}[-1/\epsilon]\) 是最小近似，不是所有实验几何下的完整截面。[Kozawa 等（1994）](https://doi.org/10.1063/1.356492)

若在窄频段内 \(R(\omega)\simeq R_0\)，则：

\[
S_{\mathrm{LOPC}}(\omega)
\propto
\frac{\epsilon''(\omega)}
{(\epsilon'(\omega))^2+(\epsilon''(\omega))^2}.
\]

仪器 Gaussian 展宽应作用于完整的耦合响应：

\[
I_{\mathrm{meas}}(\omega)=
G(\omega;\sigma_{\mathrm{inst}})*S_{\mathrm{LOPC}}(\omega)
+B(\omega).
\]

本征介电零点、损耗函数峰和实测峰分别满足不同条件：

\[
\epsilon(\omega_z)=0,
\qquad
\frac{\mathrm d}{\mathrm d\omega}
\operatorname{Im}\left[-\frac1{\epsilon(\omega)}\right]
\bigg|_{\omega=\omega_{\mathrm{loss}}}=0,
\qquad
\frac{\mathrm d I_{\mathrm{meas}}}{\mathrm d\omega}
\bigg|_{\omega=\omega_{\mathrm{peak}}}=0.
\]

\[
\omega_{\mathrm{peak}}
\neq \operatorname{Re}\omega_z
\quad\text{（有阻尼或仪器卷积时一般成立）}.
\]

不能先把 \(L^+\) 和 \(L^-\) 各自拟合成独立 Voigt，再把两个峰的宽度和面积直接解释为同一个介电模型的载流子参数；那样会丢失两分支由同一组 \(n\)、\(\gamma_p\) 和声子参数施加的物理约束。

### 2.5 参数可辨识性

从上述关系可见：

\[
\omega_p^2\propto\frac{n}{m^*},
\qquad
\gamma_p\propto\frac{1}{m^*\mu}.
\]

因此单条 Raman 线形直接约束的通常是 \(n/m^*\) 和 \(1/(m^*\mu)\)，不是完全独立的 \(n\)、\(m^*\) 与 \(\mu\)。若要反演 \(n\) 和 \(\mu\)，应固定或外部标定 \(m^*\)、\(\epsilon_\infty\)、\(\omega_{\mathrm{TO}}\)、\(\omega_{\mathrm{LO}}\) 以及散射矩阵元。扫描共焦 Raman 载流子成像也采用这类介电响应来反演空间载流子分布。[Matthews 等（2001）](https://doi.org/10.1063/1.1415421)

从数值拟合角度，令参数向量为 \(\boldsymbol\theta\)，模型为 \(I(\omega;\boldsymbol\theta)\)，局部可辨识性取决于 Jacobian：

\[
J_{ij}=\frac{\partial I(\omega_i;\boldsymbol\theta)}
{\partial\theta_j}.
\]

若 \(J\) 的列近似线性相关，或者 \((J^{\mathsf T}WJ)^{-1}\) 病态，那么增加自由参数只会制造强相关而不会增加可靠信息。LOPC 拟合中尤其要避免同时自由放开 \(m^*\)、\(\epsilon_\infty\)、声子频率、仪器宽度、背景曲率和 \(n\)。

### 2.6 n-GaN 与 p-GaN

对 n-GaN，电子有效质量较小，\(\omega_p\) 对电子浓度通常较敏感。对 p-GaN，空穴有效质量较大、各向异性和阻尼可能降低从单条线形唯一反演输运参数的能力。

Harima 等在空穴浓度约 \(5\times10^{16}\) 到 \(10^{18}\,\mathrm{cm^{-3}}\) 的 p-GaN 中发现，LOPC 线形随空穴浓度没有 n 型样品那样显著的变化。[Harima 等（1998a）](https://doi.org/10.1063/1.122348) 这不等于 p-GaN 不存在 LOPC。Demangeot 等在空穴浓度最高约 \(3\times10^{18}\,\mathrm{cm^{-3}}\) 的 p-GaN 中观测并用介电模型拟合了轴向和面内耦合模，还报告了空穴质量各向异性的证据。[Demangeot 等（1998）](https://doi.org/10.1016/S0038-1098(98)00093-3)

实际灵敏度取决于空穴浓度、迁移率、阻尼、测量几何和信噪比。Mg 掺杂浓度也不等于自由空穴浓度，补偿和激活率必须由独立电学信息约束。

## 3. 主线二：载流子引起的 Raman Fano 干涉

### 3.1 从离散态-连续态模型出发

Fano 机制要求存在两条能量重叠且不可区分的散射路径：一条经过离散声子态，另一条进入电子连续态。一个抽象的 Hamiltonian 可以写成：

\[
H=\omega_d\lvert d\rangle\langle d\rvert
+\int E\lvert E\rangle\langle E\rvert\,\mathrm dE
+\int\left[
V(E)\lvert E\rangle\langle d\rvert
+V^*(E)\lvert d\rangle\langle E\rvert
\right]\mathrm dE.
\]

这里取 \(\hbar=1\)，所以 \(E\) 和 \(\omega\) 使用同一单位。\(\lvert d\rangle\) 是离散声子态，\(\lvert E\rangle\) 是电子连续态，\(V(E)\) 是二者耦合，连续态的态密度为 \(\rho(E)\)。在宽带近似下，离散态的推迟自能为：

\[
\Sigma^R(\omega)
=
\mathcal P\!\int
\frac{\rho(E)|V(E)|^2}{\omega-E}\,\mathrm dE
-i\pi\rho(\omega)|V(\omega)|^2.
\]

\[
\omega_F\simeq\omega_d+\operatorname{Re}\Sigma^R(\omega_F),
\qquad
\frac{\Gamma_F}{2}
\simeq-\operatorname{Im}\Sigma^R(\omega_F)
=\pi\rho(\omega_F)|V(\omega_F)|^2.
\]

这个离散态-连续态干涉框架来自 Fano 的原始理论。[Fano（1961）](https://doi.org/10.1103/PhysRev.124.1866)

### 3.2 振幅相加，而不是强度相加

把共振附近的无量纲失谐定义为：

\[
\varepsilon_F=\frac{\omega-\omega_F}{\Gamma_F/2}.
\]

在最简单的单连续道、实耦合近似下，散射振幅可写成与下式等价的形式：

\[
f(\varepsilon_F)\propto
\frac{q_F+\varepsilon_F}{\varepsilon_F+i}.
\]

在一种常见的相位约定下，\(q_F\) 的来源可以概略写成：

\[
q_F\sim
\frac{
T_d+\mathcal P\!\int
\dfrac{V(E)T_c(E)}{\omega_F-E}\,\mathrm dE
}
{\pi V(\omega_F)T_c(\omega_F)}.
\]

其中 \(T_d\) 是直接激发离散态的振幅，\(T_c(E)\) 是激发连续态的振幅，\(\mathcal P\) 表示 Cauchy 主值。这个表达式的具体符号和归一化依赖态的相位约定，但它说明 \(q_F\) 同时包含相对振幅、相位和连续态重整化，不能仅凭一个拟合数值把它等同于载流子浓度。

取模平方得到标准 Fano 强度：

\[
S_F(\omega)=
I_c(\omega)
\frac{(q_F+\varepsilon_F)^2}
{1+\varepsilon_F^2}
\]

其中 \(I_c\) 是连续态强度尺度，\(q_F\) 是相对振幅和相位的无量纲参数，\(\omega_F\)、\(\Gamma_F\) 是耦合后的共振位置和宽度。标准公式中 \(q_F\) 取实数；多个连续道、额外退相干或非相干背景可能需要复数 \(q_F\)，此时理想的零强度反共振会被填平。

将强度展开为：

\[
S_F(\varepsilon_F)
=I_c
\left[
1+
\frac{q_F^2-1}{1+\varepsilon_F^2}
+
\frac{2q_F\varepsilon_F}{1+\varepsilon_F^2}
\right].
\]

其中干涉项为：

\[
S_{\mathrm{int}}(\varepsilon_F)
=I_c\frac{2q_F\varepsilon_F}
{1+\varepsilon_F^2}.
\]

直接求导：

\[
\frac{\mathrm dS_F}{\mathrm d\varepsilon_F}
=
\frac{2I_c(q_F+\varepsilon_F)(1-q_F\varepsilon_F)}
{(1+\varepsilon_F^2)^2}.
\]

所以：

\[
\varepsilon_{\mathrm{zero}}=-q_F,
\qquad
\varepsilon_{\mathrm{ext}}=\frac1{q_F}.
\]

当 \(\lvert q_F\rvert\to\infty\) 并重新归一化时：

\[
\frac{(q_F+\varepsilon_F)^2}{1+\varepsilon_F^2}
\sim
\frac{q_F^2}{1+\varepsilon_F^2},
\]

即趋近对称 Lorentzian。若 \(q_F=q_r+iq_i\) 为复数，则：

\[
S_F(\varepsilon_F)
=I_c
\frac{(\varepsilon_F+q_r)^2+q_i^2}
{1+\varepsilon_F^2},
\]

\[
q_i\neq0
\quad\Longrightarrow\quad
S_F(-q_r)=
I_c\frac{q_i^2}{1+q_r^2}>0.
\]

因此非对称峰本身只是现象，Fano 还要求上式中的复振幅交叉项存在。

### 3.3 仪器展宽后的 Fano-Voigt

如果需要考虑 Gaussian 仪器或非均匀展宽，应对完整 Fano 样品响应做卷积：

\[
I_{\mathrm{FV}}(\omega)=
G(\omega;\sigma)*S_F(\omega)+B(\omega).
\]

这才是 Fano-Voigt。它不同于把 Fano 函数和 Voigt 函数按强度直接相加，因为 Fano 的干涉项必须在卷积前保留。

若连续背景在共振窄窗口内近似常数，标准公式足够；若电子连续态本身随频率快速变化，应把 \(I_c(\omega)\) 建模为低阶平滑函数或由电子响应理论给出，而不能让一个高阶多项式任意吞掉 Fano 反共振。

### 3.4 GaN 中的证据和边界

Harima 等在 p-GaN Raman 光谱中观察到随空穴浓度增加而增强的低频连续带，并将其归因于空穴的价带间跃迁。[Harima 等（1998a）](https://doi.org/10.1063/1.122348) 同一研究组随后指出，该电子连续带与重叠的声子带发生 Fano 干涉，并提出用连续带强度及干涉特征表征空穴浓度。[Harima 等（1998b）](https://doi.org/10.1016/S0022-0248(98)00246-2)

需要保留证据边界：上述论文的公开摘要支持“p-GaN 中价带间电子连续态与重叠声子带发生 Fano 干涉”，但没有在摘要中把发生干涉的声子无歧义地指定为 \(A_1(\mathrm{LO})\)。因此本项目可以把 Fano-Voigt 作为 \(A_1(\mathrm{LO})\) 的候选模型，但不能仅凭这两篇论文就把任意 \(A_1(\mathrm{LO})\) 不对称认定为 Fano。

要把某条 \(A_1(\mathrm{LO})\) 峰解释为载流子 Fano，至少应检查：

1. 该声子频率附近是否存在可测的电子 Raman 连续态；
2. 连续态和声子是否位于兼容的偏振、动量和对称性通道；
3. \(q_F\)、\(\Gamma_F\) 和连续背景是否随空穴浓度、注入电流或激发能量系统变化；
4. 反共振方向是否在重复测量中稳定，而不是基线、空间平均或仪器响应造成；
5. 允许 LOPC 后，Fano 是否仍显著改善残差并具有稳定、有限的参数置信区间。

## 4. 两种主模型的数学区别

### 4.1 LOPC 是响应函数的谱问题

LOPC 的核心对象是同一介电函数：

\[
\epsilon(\omega;n,\mu,m^*,\gamma_{\mathrm{ph}},\ldots).
\]

耦合模由 \(\epsilon=0\) 的复根控制，Raman 强度则由 \(\operatorname{Im}[-1/\epsilon]\) 及散射矩阵元决定。改变 \(n\) 或 \(\mu\) 会同时改变根的位置、虚部和两个分支的谱权重。

### 4.2 Fano 是振幅的干涉问题

Fano 的核心对象是：

\[
f_{\mathrm{tot}}(\omega)
=f_{\mathrm{cont}}(\omega)+f_{\mathrm{ph}}(\omega),
\qquad
I(\omega)=\lvert f_{\mathrm{tot}}(\omega)\rvert^2.
\]

展开后有交叉项：

\[
I=\lvert f_{\mathrm{cont}}\rvert^2
+\lvert f_{\mathrm{ph}}\rvert^2
+2\operatorname{Re}\left(f_{\mathrm{cont}}f_{\mathrm{ph}}^*\right).
\]

正是最后一项产生了增强和抵消。把两个贡献直接按强度相加会丢掉该项，因而不能描述真正的 Fano 干涉。

### 4.3 是否可以联合

如果实验确实同时显示 LOPC 和电子连续态干涉，应写成振幅层面的示意联合模型：

\[
I(\omega)\propto
\left\lvert
\chi_{\mathrm{cont}}(\omega)
+\chi_{\mathrm{LOPC}}(\omega)
\right\rvert^2.
\]

其中 \(\chi_{\mathrm{LOPC}}\) 本身包含介电函数耦合，\(\chi_{\mathrm{cont}}\) 需要连续态的频率依赖、相位和 Raman 张量。这个模型的参数相关性很强，若没有独立的载流子浓度、偏振或激发能量数据，容易出现不可辨识。因此开发顺序应是先分别验证 LOPC 和 Fano，再考虑联合模型，而不是一开始把所有参数同时放开。

## 5. 面向 GaN LED 的拟合与判别顺序

### 5.1 模型层级

建议保留以下层级：

1. **参考模型**：Voigt，用于确认峰位、基础宽度和仪器分辨率；
2. **n-GaN 主模型**：LOPC 介电响应，再与实测或 Gaussian 仪器函数卷积；
3. **p-GaN 条件模型**：在电子连续背景有证据时使用 Fano 或 Fano-Voigt；
4. **联合研究模型**：连续态振幅与 LOPC 响应相干叠加，仅在数据和外部约束足够时使用；
5. **附录模型**：角向色散、空间平均和额外自能修正，用于解释主模型无法解释的残差。

### 5.2 n-GaN

1. 用低载流子样品确定 \(\omega_{\mathrm{TO}}\)、\(\omega_{\mathrm{LO}}\) 和声子阻尼的合理范围；
2. 优先拟合 LOPC 介电损耗形式，并固定文献或独立测量给出的 \(m^*\) 和介电常数；
3. 检查反演的 \(n\)、\(\mu\) 是否与 Hall、电容或器件结构的量级一致；
4. 只有在 LOPC、角向色散和空间平均都不能解释的连续背景及反共振结构出现时，才引入 Fano 振幅。

### 5.3 p-GaN

1. p-GaN 仍可能存在 LOPC，但空穴质量、各向异性和阻尼会降低线形反演的灵敏度；[Demangeot 等（1998）](https://doi.org/10.1016/S0038-1098(98)00093-3)
2. 检查低频电子连续带是否随空穴浓度或注入条件增强，这是采用 Fano 模型的重要前提；[Harima 等（1998a）](https://doi.org/10.1063/1.122348)
3. Mg 掺杂浓度不等于自由空穴浓度，补偿和激活率需要独立电学约束；
4. 若只有平滑偏斜峰而没有连续态证据，保留 LOPC、空间叠加和附录效应作为竞争解释。

### 5.4 参数和单位

LOPC 的最小参数通常为：

- 载流子浓度 \(n\)；
- 载流子阻尼 \(\gamma_p\)，或在固定 \(m^*\) 后用迁移率 \(\mu\)；
- 声子阻尼 \(\gamma_{\mathrm{ph}}\)；
- 总强度和小幅频率标定偏移；
- 最好由标准样品预先固定的仪器 Gaussian 宽度。

以下量不宜全部自由变化：\(m^*\)、\(\epsilon_\infty\)、\(\omega_{\mathrm{TO}}\)、\(\omega_{\mathrm{LO}}\)、Faust-Henry/散射矩阵元系数、背景曲率和仪器宽度。

Fano 的最小参数为 \(\omega_F\)、\(\Gamma_F\)、\(q_F\)、连续背景尺度及其必要的平滑频率依赖。\(q_F\) 是相位和相对振幅参数，不应未经模型推导就直接当作载流子浓度。

介电函数和等离子频率天然使用角频率 \(\mathrm{rad\,s^{-1}}\)，而 Raman 横轴通常是波数 \(\mathrm{cm^{-1}}\)：

\[
\omega=2\pi c\,\widetilde\nu.
\]

不能把以 \(\mathrm{cm^{-1}}\) 表示的峰位直接代入 SI 的等离子频率公式。可以在内部全部转换为角频率，计算完后再转换回 Raman shift；或者从头到尾使用一致的波数形式，并同步转换所有阻尼参数。

### 5.5 物理解释的最低证据

较小的 chisqr、AIC 或 BIC 只能说明曲线拟合得更好，不能单独确认机制。至少还应满足：

- 参数远离人为边界且置信区间有限；
- 多个空间点或重复测量中参数连续、可重复；
- LOPC 的 \(n\)、\(\mu\) 与独立电学测量量级相符；
- Fano 的 \(q_F\) 与连续背景、激发能量或载流子条件同步变化；
- 改变偏振、数值孔径或入射几何后，附录效应可以被区分；
- 模型能预测未参与拟合的谱线或实验条件，而不只是降低当前曲线残差。

## 附录 A：次要或替代解释

下面的效应保留在文档中，但不与 LOPC、Fano 并列作为本专题的主要模型。

### A.1 载流子引起的声子自能

即使没有可辨认的 LOPC 双分支或 Fano 反共振，电子-声子相互作用也会通过声子自能改变峰位和线宽。采用 \(\exp(-i\omega t)\) 的推迟传播子可以写成：

\[
D^R(\omega)=
\frac{2\omega_0}
{\omega^2-\omega_0^2+i\gamma_0\omega
-2\omega_0\Sigma^R(\omega)},
\]

\[
\Sigma^R(\omega)=
\Delta(\omega)-\frac{i}{2}\Gamma_{\mathrm{e-ph}}(\omega).
\]

\(\Delta\) 改变峰位，\(\Gamma_{\mathrm{e-ph}}\) 改变线宽。若自能在峰附近变化缓慢，结果仍可能近似为移动、展宽后的 Lorentzian/Voigt；只有连续态的频率依赖和相干干涉不可忽略时，才需要 Fano。因而“峰位或 FWHM 随载流子变化”本身不能证明 Fano，也可能来自 LOPC、普通自能重整化、温升或应变变化。

### A.2 A1(LO) 的角向色散

纤锌矿 GaN 是非立方晶体。有限数值孔径、样品倾斜、晶面取向和偏振几何会使实验收集一组不同传播方向的 LO 声子响应：

\[
I_{\mathrm{ang}}(\omega)=
\int P(\theta,\phi)
I_{A_1(\mathrm{LO})}(\omega;\theta,\phi)
\,\mathrm d\Omega.
\]

Shi、Ponce 和 Menéndez 的高分辨 Raman 实验表明，GaN \(A_1(\mathrm{LO})\) 的复杂线形可以由 LO 声子的角向色散解释，并据此提取更接近时域测量的本征非简谐线宽。[Shi 等（2004）](https://doi.org/10.1063/1.1737792)

如果改变数值孔径、入射角或偏振而不改变电学条件时，不对称明显变化，应先检验角向积分，而不是立即归因于载流子 Fano。

### A.3 空间和深度平均

完整 LED 的激光焦体积可能同时包含 p-GaN、量子阱、n-GaN、缓冲层和衬底。载流子浓度、应变、温度和光学权重随位置变化时，像素信号更接近：

\[
I_{\mathrm{pixel}}(\omega)=
\int W(\mathbf r)I(\omega;\mathbf r)\,\mathrm d^3\mathbf r.
\]

一组局部对称线形的空间平均也能产生表观不对称。因此逐像素自由拟合复杂模型前，应检查相邻像素参数连续性，并用器件层结构约束可能出现的谱线成分。

### A.4 基线、仪器和 Voigt 近似

airPLS 只能估计预处理背景，不能替代电子连续态模型。仪器 Gaussian 展宽应对完整 LOPC 或 Fano 响应卷积，不能用基线或独立峰宽吸收真实的物理结构。Voigt 是参考模型，不应被当作 LOPC 或 Fano 的物理解释。

## 实施结果：物理先验初值与边界敏感性分析

本节记录将前述 LOPC 物理模型应用到当前扫描数据后的第一轮数值检验。目标峰已确定为掺杂 p-GaN 的 \(A_1(\mathrm{LO})\) 峰；本节不重新讨论峰的归属，只检验在物理先验初值下，当前最小 LOPC 线型能否稳定反演载流子相关参数。

### 0. 面向外部物理咨询的摘要

对当前 \((x=0,y=0)\) 光谱的测试表明：改变载流子浓度、迁移率所对应的初始参数后，非线性最小二乘拟合都回到相近的强阻尼区域。因此，当前现象不是“初值选错”这么简单，而是数据窗口与最小 LOPC 模型之间存在参数退化或结构不匹配。

需要区分以下三类结论：

1. \(\omega_{\mathrm l}\approx735~\mathrm{cm^{-1}}\) 与已知的掺杂 GaN \(A_1(\mathrm{LO})\) 峰位置相容；
2. \(\omega_{\mathrm p}\) 和 \(\gamma_{\mathrm p}\) 的数量级可以作条件性的载流子参数参考，但目前不能视为由 Raman 单条谱线独立测得的 \(n\) 和 \(\mu\)；
3. \(\gamma_{\mathrm{ph}}\) 被推到极小值，尤其是无边界拟合得到的 \(2.5\times10^{-5}~\mathrm{cm^{-1}}\)，不能解释为真实的 GaN 本征声子线宽。它更可能是在补偿未建模的仪器展宽、局部背景或其它峰的尾部。

因此，当前结果支持“该谱窗与掺杂 GaN 的 LOPC 响应相容”，但不支持仅凭这条谱线唯一反演自由载流子浓度、迁移率和本征声子阻尼。

### 1. 数据和拟合设置

测试使用校正光谱 work/baseline/output/corrected.tif 的 \((x=0,y=0)\) 点，在 \(720\)--\(750~\mathrm{cm^{-1}}\) 窗口内拟合。窗口包含 100 个采样点，采样间隔约 \(0.3006~\mathrm{cm^{-1}}\)，观测强度最大值位于约 \(735.07~\mathrm{cm^{-1}}\)。

固定参数为：

\[
\omega_{\mathrm T}=533~\mathrm{cm^{-1}},\qquad
\epsilon_\infty=9.5.
\]

为了避免把数值优化跑到明显不合理的区域，LM 拟合暂时使用如下边界：

| 参数 | 边界 |
|---|---:|
| \(I_0\)（amplitude） | \(0\) 到初始幅度的 10 倍（至少为 1） |
| \(\omega_{\mathrm p}\) | \(0\)--\(700~\mathrm{cm^{-1}}\) |
| \(\gamma_{\mathrm p}\) | \(20\)--\(5000~\mathrm{cm^{-1}}\) |
| \(\gamma_{\mathrm{ph}}\) | \(0.5\)--\(20~\mathrm{cm^{-1}}\) |
| \(\omega_{\mathrm l}\) | \(720\)--\(750~\mathrm{cm^{-1}}\) |

Adam 阶段若启用，也必须使用与 LM 相同的物理可行域；否则 Adam 得到的初值在 LM 阶段仍可能离开该区域。

### 2. 物理先验初值

由于当前样品按 p-GaN 处理，下面的第一轮换算仍暂时取 \(m^*=0.2m_0\)、\(\epsilon_\infty=9.5\) 作为数值参照，而不是 p-GaN 的最终物理先验。实际 p-GaN 应使用空穴有效质量、空穴迁移率和自由空穴浓度；空穴有效质量具有各向异性，且 Mg 掺杂浓度不等于自由空穴浓度。使用的换算关系为

\[
\omega_{\mathrm p}=\frac{1}{2\pi c}\sqrt{\frac{ne^2}{\epsilon_0\epsilon_\infty m^*}},\qquad
\gamma_{\mathrm p}=\frac{1}{2\pi c\tau}=\frac{e}{2\pi c\,m^*\mu}.
\]

这里的 \(n\) 用 \(\mathrm{cm^{-3}}\)、\(\mu\) 用 \(\mathrm{cm^2/(V\,s)}\) 时，计算结果再换算为 \(\mathrm{cm^{-1}}\)。测试的初值为：

| 假设 | \(\omega_{\mathrm p,0}\) | \(\gamma_{\mathrm p,0}\) | \(\gamma_{\mathrm{ph},0}\) | \(\omega_{\mathrm l,0}\) |
|---|---:|---:|---:|---:|
| \(n=10^{17}~\mathrm{cm^{-3}},\ \mu=200\) | 68.7 | 233 | 4 | 734 |
| \(n=10^{18}~\mathrm{cm^{-3}},\ \mu=100\) | 217 | 467 | 4 | 734 |
| \(n=3\times10^{18}~\mathrm{cm^{-3}},\ \mu=30\) | 376 | 1556 | 5 | 734 |
| \(n=3\times10^{18}~\mathrm{cm^{-3}},\ \mu=10\) | 376 | 4669 | 7 | 734 |

这些数值只是为了测试优化器对不同数量级初值的响应，并不是当前 p-GaN 样品的可信载流子先验。对于 p-GaN，应使用独立电学测量或文献中与样品生长条件相符的空穴有效质量、自由空穴浓度和迁移率；Mg 掺杂浓度不能直接当作自由空穴浓度。

### 3. 拟合结果

四组不同初值均收敛到几乎相同的结果：

\[
\begin{aligned}
\omega_{\mathrm l}&\simeq735.30~\mathrm{cm^{-1}},\\
\omega_{\mathrm p}&\simeq425~\mathrm{cm^{-1}},\\
\gamma_{\mathrm p}&\simeq5000~\mathrm{cm^{-1}},\\
\gamma_{\mathrm{ph}}&\simeq0.5~\mathrm{cm^{-1}},\\
\mathrm{RMSE}&\simeq0.7452.
\end{aligned}
\]

其中 \(\gamma_{\mathrm p}\) 撞到上边界，\(\gamma_{\mathrm{ph}}\) 撞到下边界。作为比较，原先没有这些有限边界的结果为：

\[
\omega_{\mathrm p}\simeq354.6,\quad
\gamma_{\mathrm p}\simeq3268.5,\quad
\gamma_{\mathrm{ph}}\simeq2.5\times10^{-5},\quad
\omega_{\mathrm l}\simeq734.60,\quad
\mathrm{RMSE}\simeq0.7444.
\]

因此，换用物理先验初值并没有把解带到另一个局部极小值；不同初值最终都进入同一个强阻尼区域。将 \(\gamma_{\mathrm{ph}}\) 固定为更常见的 \(2\)--\(7~\mathrm{cm^{-1}}\) 后，RMSE 约为 \(0.749\)--\(0.762\)，且 \(\gamma_{\mathrm p}\) 仍倾向于增大。

### 4. 物理解释和限制

在上述仅用于数值参照的质量参数下，\(\omega_{\mathrm p}\simeq425~\mathrm{cm^{-1}}\) 会对应约数 \(10^{18}~\mathrm{cm^{-3}}\) 的自由载流子浓度，\(\gamma_{\mathrm p}\simeq5000~\mathrm{cm^{-1}}\) 会对应约为 \(10~\mathrm{cm^2/(V\,s)}\) 的迁移率。但对于当前 p-GaN，这两个换算都不能直接作为定量结论：空穴有效质量、各向异性、补偿程度和激活率都会改变结果。特别是，不能把 Mg 掺杂浓度直接代入等离子频率公式。

这里的 \(\gamma_{\mathrm p}\) 是载流子动量弛豫率，不是 Raman 峰的直接 FWHM。它很大时表示等离激元可能处于过阻尼状态，两个理想耦合分支可以不再清楚分辨。拟合中 \(\gamma_{\mathrm p}\) 撞到上边界，只能说明在当前窗口和模型中“继续增大阻尼仍有利于降低残差”；不能把 \(5000~\mathrm{cm^{-1}}\) 当作已经测定的材料常数。

\(\gamma_{\mathrm{ph}}\) 接近 \(0.5~\mathrm{cm^{-1}}\) 也应谨慎解释。它的数值尺度只有约 1--2 个采样间隔；更重要的是，\(\gamma_{\mathrm{ph}}\) 不是在没有仪器函数时就能直接等同于观测 FWHM 的量。无边界结果进一步把它压到 \(2.5\times10^{-5}~\mathrm{cm^{-1}}\)，这已经是一个明确的可辨识性和模型完整性警告。

### 4.1 为什么缺少仪器卷积可能不是小修正

实际测量谱应写成

\[
I_{\mathrm{obs}}(\omega)=
G_{\sigma_{\mathrm{inst}}}*I_{\mathrm{intrinsic}}(\omega)
+B(\omega),
\]

其中 \(G_{\sigma_{\mathrm{inst}}}\) 是仪器线扩散函数，\(B\) 是局部背景。若本征峰宽远大于仪器宽度，忽略卷积通常只是近似；若本征峰宽与仪器宽度相当或更窄，卷积会改变峰高、峰宽和峰形。此时一个没有卷积的模型可能把 \(\gamma_{\mathrm{ph}}\) 压到接近零，再用强度和载流子阻尼参数去补偿仪器造成的展宽。

当前数据的采样间隔约为 \(0.3006~\mathrm{cm^{-1}}\)，但采样间隔不等于仪器分辨率。若仪器分辨率是数个 \(\mathrm{cm^{-1}}\)，那么 \(0.5~\mathrm{cm^{-1}}\) 的本征阻尼已经不能凭这段数据可靠测量。因而本次拟合中的极小 \(\gamma_{\mathrm{ph}}\) 不能被当作实验发现的超窄声子线宽。

此外，当前流程把 LOPC 窗口从其它峰的拟合区间中分离出来，未在同一个目标函数中同时加入局部背景和其它 Lorentzian 分量在该窗口内的尾部。缺少卷积并不是唯一的误差来源；仪器响应、背景和峰尾部可能共同造成参数退化。

### 5. 实施结论和下一步

这次检验说明当前困难主要不是初值，而是最小 LOPC 模型与窗口内实际信号之间的结构不匹配。后续实施应按以下顺序进行：

1. 在 Adam 和 LM 中共享同一组有限边界；
2. 将 LOPC、局部背景以及其它峰在 LOPC 窗口内的尾部放入同一个联合模型；
3. 对完整 LOPC 响应加入实测或独立标定的 Gaussian 仪器响应卷积；
4. 用 Hall 测量或其它电学数据约束自由空穴浓度 \(p\) 和迁移率 \(\mu_h\)，再换算为 \(\omega_{\mathrm p}\) 和 \(\gamma_{\mathrm p}\)；
5. 在参数撞边界时报告“模型/数据约束不足”，不要把边界值直接解释成材料常数。

在完成局部背景和仪器卷积前，当前拟合可以支持“该窗口与掺杂 p-GaN 的 LOPC 线型相容”，但还不足以支持从单条光谱唯一反演自由空穴浓度、空穴迁移率或本征声子阻尼。

## 参考文献

1. T. Kozawa, T. Kachi, H. Kano, Y. Taga, M. Hashimoto, N. Koide, and K. Manabe, “Raman scattering from LO phonon-plasmon coupled modes in gallium nitride,” *Journal of Applied Physics* **75**, 1098–1101 (1994). [DOI: 10.1063/1.356492](https://doi.org/10.1063/1.356492)
2. F. Demangeot, J. Frandon, M. A. Renucci, C. Meny, O. Briot, and R. L. Aulombard, “Interplay of electrons and phonons in heavily doped GaN epilayers,” *Journal of Applied Physics* **82**, 1305–1309 (1997). [DOI: 10.1063/1.365903](https://doi.org/10.1063/1.365903)
3. N. Wieser, M. Klose, R. Dassow, F. Scholz, and J. Off, “Raman studies of longitudinal optical phonon-plasmon coupling in GaN layers,” *Journal of Crystal Growth* **189–190**, 661–665 (1998). [DOI: 10.1016/S0022-0248(98)00242-5](https://doi.org/10.1016/S0022-0248(98)00242-5)
4. H. Harima, T. Inoue, S. Nakashima, K. Furukawa, and M. Taneya, “Electronic properties in p-type GaN studied by Raman scattering,” *Applied Physics Letters* **73**, 2000–2002 (1998). [DOI: 10.1063/1.122348](https://doi.org/10.1063/1.122348)
5. H. Harima, H. Sakashita, T. Inoue, and S. Nakashima, “Electronic properties in doped GaN studied by Raman scattering,” *Journal of Crystal Growth* **189–190**, 672–676 (1998). [DOI: 10.1016/S0022-0248(98)00246-2](https://doi.org/10.1016/S0022-0248(98)00246-2)
6. F. Demangeot, J. Frandon, M. A. Renucci, N. Grandjean, B. Beaumont, J. Massies, and P. Gibart, “Coupled longitudinal optic phonon-plasmon modes in p-type GaN,” *Solid State Communications* **106**, 491–494 (1998). [DOI: 10.1016/S0038-1098(98)00093-3](https://doi.org/10.1016/S0038-1098(98)00093-3)
7. L. Shi, F. A. Ponce, and J. Menéndez, “Raman line shape of the A1 longitudinal optical phonon in GaN,” *Applied Physics Letters* **84**, 3471–3473 (2004). [DOI: 10.1063/1.1737792](https://doi.org/10.1063/1.1737792)
8. M. J. Matthews, J. W. P. Hsu, S. Gu, and T. F. Kuech, “Carrier density imaging of lateral epitaxially overgrown GaN using scanning confocal Raman microscopy,” *Applied Physics Letters* **79**, 3086–3088 (2001). [DOI: 10.1063/1.1415421](https://doi.org/10.1063/1.1415421)
9. U. Fano, “Effects of Configuration Interaction on Intensities and Phase Shifts,” *Physical Review* **124**, 1866–1878 (1961). [DOI: 10.1103/PhysRev.124.1866](https://doi.org/10.1103/PhysRev.124.1866)

## 附录 B：供物理学教授讨论的 p-GaN \(A_1(\mathrm{LO})\) 线形简报

### B.1 问题和最小模型

样品按 p-GaN 处理，目标谱带已经确定为掺杂 GaN 的 \(A_1(\mathrm{LO})\) 峰。这里希望判断：该峰是否可以用 LO 声子与自由空穴等离激元耦合（LOPC）解释，以及 Raman 线形是否能够给出自由空穴浓度或输运阻尼的可靠信息。

当前使用的最小模型先写成复介电函数

\[
\epsilon(\omega)=\epsilon_\infty
\left[
1+
\frac{\omega_{\mathrm L}^{2}-\omega_{\mathrm T}^{2}}
{\omega_{\mathrm T}^{2}-\omega^{2}-i\omega\gamma_{\mathrm{ph}}}
-
\frac{\omega_{\mathrm p}^{2}}
{\omega(\omega+i\gamma_{\mathrm p})}
\right],
\]

并用介电损耗函数表示 Raman 响应：

\[
I_{\mathrm{min}}(\omega)=
I_0\,\operatorname{Im}\left[-\frac{1}{\epsilon(\omega)}\right].
\]

这里的 \(\omega=2\pi c\widetilde\nu\)，\(\widetilde\nu\) 是 Raman 位移。下文的数值统一写成等效的 \(\mathrm{cm^{-1}}\) 频移，实际计算时必须保持角频率与阻尼使用同一单位。这个表达式是最小响应模型，尚未包含 Faust--Henry 散射因子、Fano 连续态、局部背景或仪器线形卷积。

### B.2 参数的物理含义

| 符号 | 物理含义 |
|---|---|
| \(I_0\) | 总 Raman 强度尺度，包含散射几何和其它整体强度因素 |
| \(\omega_{\mathrm L}\) | 无自由载流子时的纵向光学声子频率；在模型中是 LO 声子的参考频率 |
| \(\omega_{\mathrm T}\) | 横向光学声子频率，本次计算固定为约 \(533~\mathrm{cm^{-1}}\) |
| \(\omega_{\mathrm p}\) | 屏蔽等离子频率；对 p-GaN 由自由空穴浓度和空穴有效质量决定 |
| \(\gamma_{\mathrm p}\) | 自由空穴动量弛豫率，不是 Raman 峰的直接 FWHM；越大表示等离激元阻尼越强 |
| \(\gamma_{\mathrm{ph}}\) | LO 声子阻尼参数，描述本征声子响应的耗散 |
| \(\epsilon_\infty\) | 高频介电常数，本次计算固定为约 9.5 |

对于 p-GaN，若采用 SI 定义，相关数量级关系为

\[
\omega_{\mathrm p}^{2}
\simeq
\frac{p e^2}{\epsilon_0\epsilon_\infty m_h^*},
\qquad
\gamma_{\mathrm p}
\simeq
\frac{e}{m_h^*\mu_h},
\]

其中 \(p\) 是自由空穴浓度，\(m_h^*\) 是相应方向的空穴有效质量，\(\mu_h\) 是空穴迁移率。Mg 掺杂浓度不能直接代替 \(p\)，因为补偿和激活率会使二者不同。p-GaN 的空穴有效质量还可能具有各向异性，因此不能无条件套用电子型 GaN 的参数。

### B.3 当前数据和现象

使用校正光谱中 \((x=0,y=0)\) 的代表性单点，在 \(720\)--\(750~\mathrm{cm^{-1}}\) 范围内观察到峰最大值约为 \(735.07~\mathrm{cm^{-1}}\)。本次计算固定 \(\omega_{\mathrm T}=533~\mathrm{cm^{-1}}\) 和 \(\epsilon_\infty=9.5\)。

从几组不同载流子数量级的初始估计出发，结果都回到相近的参数区域：

\[
\omega_{\mathrm l}\approx735.3~\mathrm{cm^{-1}},
\qquad
\omega_{\mathrm p}\approx425~\mathrm{cm^{-1}},
\]

同时，\(\gamma_{\mathrm p}\) 倾向于继续增大，\(\gamma_{\mathrm{ph}}\) 倾向于继续减小。将这些参数完全交给当前最小模型时，曾得到

\[
\gamma_{\mathrm p}\approx3268~\mathrm{cm^{-1}},
\qquad
\gamma_{\mathrm{ph}}\approx2.5\times10^{-5}~\mathrm{cm^{-1}}.
\]

这说明当前谱线对 \(\gamma_{\mathrm p}\) 的上限和 \(\gamma_{\mathrm{ph}}\) 的下限都缺少足够约束；不同先验数量级的试算也没有把结果带到明显不同的稳定区域。

### B.4 目前可以怎样解释

1. **峰位方面**：\(\omega_{\mathrm l}\) 位于约 \(735~\mathrm{cm^{-1}}\)，与 p-GaN 中 \(A_1(\mathrm{LO})\) 候选峰的数量级一致。
2. **等离子频率方面**：\(\omega_{\mathrm p}\) 的数值只有在给定空穴有效质量、自由空穴浓度和介电常数定义后才可换算为载流子信息。当前使用的电子型质量只是数值参照，不能当作 p-GaN 的真实物理先验。
3. **载流子阻尼方面**：较大的 \(\gamma_{\mathrm p}\) 表示强阻尼或过阻尼等离激元，不能直接等同于一个同样宽的 Raman 峰。拟合倾向于增大它，说明当前谱窗对其上限缺乏约束。
4. **声子阻尼方面**：\(\gamma_{\mathrm{ph}}\) 被压到极小值不能作为“本征声子极窄”的证据。当前模型没有显式包含仪器展宽；如果仪器分辨率与本征峰宽相当，模型可能用接近零的本征阻尼去代替实际仪器卷积。
5. **可辨识性方面**：单条谱线、有限频率窗口和最小介电损耗模型不足以保证 \(p\)、\(\mu_h\)、\(\gamma_{\mathrm{ph}}\) 能被分别确定。当前结果更适合被称为“与强阻尼 LOPC 线形相容”，而不是对这些物理量的唯一测量。

### B.5 希望请教的问题

1. 对该 p-GaN 样品，合理的空穴有效质量张量、自由空穴浓度和迁移率范围应如何取？是否有 Hall 或其它电学数据可以作为约束？
2. 上式中的 \(\omega_{\mathrm p}\) 应采用屏蔽等离子频率，还是应改用未除以 \(\epsilon_\infty\) 的裸等离子频率？
3. 在约 \(735~\mathrm{cm^{-1}}\) 处，实验系统的实际仪器线形和分辨率是多少？是否有标准样品或窄参考峰可用于标定？
4. 对 p-GaN 的 \(A_1(\mathrm{LO})\)，最小的 \(\operatorname{Im}[-1/\epsilon]\) 响应是否足够，还是应包含 Faust--Henry 因子、Fano 连续态、角向色散或深度平均？
5. 仅凭当前线形，怎样区分 LOPC、Fano 干涉、声子自能和仪器/空间平均造成的表观展宽或不对称？

这份简报的目的不是把当前数值结果作为最终材料参数，而是请教授判断：p-GaN 的物理先验和完整 Raman 响应模型应如何建立，哪些独立实验量最值得优先测量。
