# GaN A1(LO) 载流子效应专题：LOPC 与 Raman Fano 干涉

本文说明物理机制、参数含义与结果解释条件。线型的完整代数表达、单位和数学可辨识性见《[GaN A1LO 拟合数学模型](GaN_A1LO_拟合数学模型.md)》；脚本配置与运行命令见各目录 README，实验与咨询记录见 [reports](../reports/README.md)。

## 0. 阅读方式与范围

本文只把下面两种机制作为正文的主线：

1. **LO 声子-等离激元耦合（LOPC）**：载流子集体振荡与极性 LO 声子通过纵向电场耦合，改变系统的本征模。数学上首先是复介电函数 \(\epsilon(\omega)\) 的零点（或相应响应函数的极点）问题。
2. **载流子引起的 Raman Fano 干涉**：离散声子散射振幅与电子连续态散射振幅相干叠加。数学上必须先相加复振幅，再取模平方。

角向色散、普通声子自能、空间不均匀性和仪器展宽也可能改变峰形，但它们不是本文的同等主线，统一放在文末附录，主要用于排除误判。

为便于推导，全文默认：

- \(\omega\) 表示角频率，时间因子采用 \(\exp(-i\omega t)\)；
- Raman 横轴若使用波数 \(\widetilde\nu\)（\(\mathrm{cm^{-1}}\)），最后再用 \(\omega=2\pi c\widetilde\nu\) 转换；
- “峰位”指响应函数的峰位置，不自动等同于介电函数零点的实部；阻尼和仪器卷积会使二者不同；
- 基线扣除属于预处理；电子 Raman 连续态若参与散射干涉，应作为样品响应的一部分，不能当作无关背景直接扣除。

对数学读者，最重要的区别可以先写成：

\[
\text{LOPC:}\quad \epsilon(\omega; n,\mu,\ldots)=0,
\qquad
\text{Fano:}\quad I(\omega)\propto
\left\lvert f_{\mathrm{cont}}(\omega)+f_{\mathrm{ph}}(\omega)\right\rvert^2.
\]

前者改变的是耦合系统的谱结构，后者改变的是两条散射路径之间的交叉项。

### 0.1 LOPC／FH 参数的物理意义

**omega_p（\(\omega_p\)）**：载流子的屏蔽等离子频率。自由载流子集体振荡的频率尺度，由浓度、有效质量与高频屏蔽共同决定；不是裸等离子频率，也不是耦合 Raman 峰位。

**gamma_p（\(\gamma\)）**：载流子阻尼。Drude 模型中对应动量弛豫率 \(1/\tau_p\)，由有效质量与迁移率决定；越大表示载流子散射越强、弛豫越快，不等于 Raman 峰的 FWHM。

**gamma_ph（\(\Gamma\)）**：声子阻尼。描述晶格振子响应的耗散，可包含非谐衰减、缺陷等贡献；同时进入介电函数和 Faust–Henry 因子，影响本征共振与散射线型，不能直接当作耦合峰的实测宽度。

**omega_l（\(\omega_L\)）**：无自由载流子耦合时的 LO 声子参考频率。对应极性晶格的纵向本征响应，可受应变和温度影响；通常不同于有载流子时的 LOPC 峰顶。

**omega_t（\(\omega_T\)）**：无自由载流子耦合时的 TO 声子参考频率。对应横向晶格振子；\(\omega_L^2-\omega_T^2\) 控制介电模型中的极性振子强度。

**epsilon_inf（\(\epsilon_\infty\)）**：高频背景相对介电常数。主要表示束缚电子的极化与背景屏蔽；显式的声子、Drude 响应另列于介电函数中，不是包含这些低频贡献的静态介电常数。

**amplitude（\(I_0\)）**：LOPC／FH 的整体 Raman 强度系数。包含激光强度、收集效率、散射几何及整体散射强度；不等于曲线峰顶高度，未经强度标定不能直接解释为载流子浓度。

**C（\(C\)）**：Faust–Henry 相对散射系数。描述形变势与电光散射的相对贡献及干涉；有符号，改变散射效率随频率的分布，正负不能由总强度非负条件决定。

**sigma_inst（\(\sigma_{\mathrm{inst}}\)）**：Gaussian 仪器响应的标准差。描述观测响应的展宽；未经仪器标定时，拟合值只能作有效 Gaussian 展宽，可能吸收未分辨的其他展宽贡献。

背景系数 \(\beta_k\) 描述平滑背景；\(\omega_c\) 是背景基函数的参考坐标。权重参数 \(\alpha\)、`scale` 控制数值目标中的强度权重。这些量均不是声子或载流子的材料参数。单位与代码符号对应见数学文档第 0 节。

下文推导中的记号对应：\(\omega_{\mathrm{LO}}=\omega_L\)、\(\omega_{\mathrm{TO}}=\omega_T\)、\(\gamma_{\mathrm{ph}}=\Gamma\)、\(\gamma_p=\gamma\)。

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
=A\,[G(\omega;\sigma)*L(\omega;\omega_0,\kappa)].
\]

其中 \(\omega_0\) 为孤立参考共振的中心，\(A\) 为面积强度系数，\(\sigma\) 为 Gaussian 标准差：

\[
L(\omega;\omega_0,\kappa)
=
\frac{1}{\pi}
\frac{\kappa}
{(\omega-\omega_0)^2+\kappa^2},
\qquad
\kappa=\mathrm{HWHM}.
\]

\(\kappa\) 是参考 Lorentzian 的半高半宽；介电模型的 \(\Gamma=\gamma_{\mathrm{ph}}\) 是振子方程中的阻尼系数。无载流子、窄共振且散射效率近似常数时，\(\kappa\simeq\Gamma/2\)，不能把二者混作同一个参数。

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
- \(\omega_p\)：包含高频屏蔽的等离子频率，\(\omega_p^2=ne^2/(\epsilon_0\epsilon_\infty m^*)\)；
- \(\gamma_p=1/\tau\)：载流子动量弛豫率。

在 SI 单位下：

\[
\omega_p^2=
\frac{n e^2}{\epsilon_0\epsilon_\infty m^*},
\qquad
\gamma_p=\frac{1}{\tau}=
\frac{e}{m^*\mu}.
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
I_0\,[n_B(\omega,T)+1]
R(\omega)
\operatorname{Im}\left[-\frac{1}{\epsilon(\omega)}\right].
\]

其中：

\[
n_B(\omega,T)=
\frac{1}{\exp(\hbar\omega/k_B T)-1}
\]

是 Stokes 散射的 Bose 因子，\(R(\omega)\) 代表 Raman 散射矩阵元、偏振几何以及形变势和电光散射贡献。Kozawa 等指出，形变势和电光机制会影响 GaN 耦合模 Raman 强度，因此 \(\operatorname{Im}[-1/\epsilon]\) 是最小近似，不是所有实验几何下的完整截面。[Kozawa 等（1994）](https://doi.org/10.1063/1.356492)

Faust–Henry A 项保留形变势散射与电光散射的相对贡献和干涉：

\[
I_A=I_0A_{\mathrm{FH}}\operatorname{Im}[-1/\epsilon],
\qquad A_{\mathrm{FH}}=1+C a_1(\omega)+C^2a_2(\omega).
\]

一次 C 项体现干涉，二次项保留相对散射强度；\(C=0\) 恢复纯介电损耗形式。若 \(A_{\mathrm{FH}}\) 在窗口内近似常数，可并入整体强度系数；否则省略它会改变线型，使其他参数代偿散射效率的频率依赖。完整函数见数学文档第 3 节；来源为《[Raman Scattering Characterization of Hexagonal GaN Layer on Sapphire Substrate](trnit1999_195-220.pdf)》印刷页 197 式 (3.2)–(3.5)。

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
\omega_p^2\propto\frac{n}{\epsilon_\infty m^*},
\qquad
\gamma_p\propto\frac{1}{m^*\mu}.
\]

因此单条 Raman 线形直接约束的通常是 \(n/(\epsilon_\infty m^*)\) 和 \(1/(m^*\mu)\)，不是完全独立的 \(n\)、\(m^*\)、\(\epsilon_\infty\) 与 \(\mu\)。反演材料性质需要相应的质量、介电常数与参考声子信息；增加自由参数不自动增加独立的物理信息。扫描共焦 Raman 载流子成像也采用这类介电响应反演空间分布。[Matthews 等（2001）](https://doi.org/10.1063/1.1415421)

数学上的精确退化和近似退化见数学文档第 8 节；反演后的材料解释见第 5 节。

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

需要保留证据边界：上述论文的公开摘要支持“p-GaN 中价带间电子连续态与重叠声子带发生 Fano 干涉”，但没有在摘要中把发生干涉的声子无歧义地指定为 \(A_1(\mathrm{LO})\)。Fano-Voigt 可以作为候选模型，但不能仅凭这两篇论文就把任意 \(A_1(\mathrm{LO})\) 不对称认定为 Fano。

要把某条 \(A_1(\mathrm{LO})\) 峰解释为载流子 Fano，至少应检查：

1. 该声子频率附近是否存在可测的电子 Raman 连续态；
2. 连续态和声子是否位于兼容的偏振、动量和对称性通道；
3. \(q_F\)、\(\Gamma_F\) 和连续背景是否随空穴浓度、注入电流或激发能量系统变化；
4. 反共振方向是否在重复测量中稳定，而不是基线、空间平均或仪器响应造成；
5. 允许 LOPC 后，Fano 是否仍显著改善残差并具有稳定、有限的参数置信区间。

Fano 参数的物理意义：

**\(\omega_F\)**：离散态与连续态耦合后的共振参考频率，包含自能造成的频移。

**\(\Gamma_F\)**：Fano 共振分母中的宽度参数；不直接等于非对称强度曲线的 FWHM，也不同于 LOPC 的 \(\Gamma\)。

**\(q_F\)**：离散态与连续态散射的相对振幅和相位参数，控制不对称及反共振；不是载流子浓度的直接读数。

**\(I_c\)**：电子连续态的 Raman 强度尺度；将真实连续态当作背景扣除会改变干涉模型的物理含义。

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

其中 \(\chi_{\mathrm{LOPC}}\) 本身包含介电函数耦合，\(\chi_{\mathrm{cont}}\) 需要连续态的频率依赖、相位和 Raman 张量。该模型增加了相对相位和连续态自由度；若缺少独立载流子、偏振或激发能量信息，不同参数可能描述近似相同的响应。

## 5. 拟合参数的物理解释边界

### 5.1 浓度、迁移率与材料条件

单载流子 Drude 模型中：

\[
\omega_p^2=\frac{ne^2}{\epsilon_0\epsilon_\infty m^*},
\qquad
\gamma=\frac1{\tau_p}=\frac{e}{m^*\mu}.
\]

**\(n\)**：参与该响应的自由载流子浓度，不等于 Mg 等掺杂原子的浓度。

**\(m^*\)**：相应载流子及响应方向的有效质量；不能将 n-GaN 的电子质量直接用于 p-GaN 空穴。

**\(\mu\)**：该 Drude 响应对应的迁移率；与独立电学值比较时须考虑载流子类型、温度和方向。

光谱首先约束 \(n/(\epsilon_\infty m^*)\) 与 \(1/(m^*\mu)\)。没有独立的质量、介电常数和材料条件，不能把 \(\omega_p\)、\(\gamma\) 唯一转换成 \(n\)、\(\mu\)。p-GaN 的较大空穴质量和阻尼还会降低这种反演的灵敏度，见第 2.6 节。

### 5.2 阻尼、寿命与实测峰宽

对孤立、弱阻尼的晶格振子：

\[
\ddot Q+\Gamma\dot Q+\omega_T^2Q=0,
\qquad
Q(t)\propto e^{-\Gamma t/2}\cos(\omega_dt+\phi),
\]

\[
\tau_{\mathrm{amplitude}}=\frac2\Gamma,
\qquad
\tau_{\mathrm{energy}}=\frac1\Gamma.
\]

上式使用角频率阻尼。无载流子、窄峰且散射因子近似常数时：

\[
\mathrm{FWHM}_{\mathrm{intrinsic}}\simeq\Gamma,
\qquad
\mathrm{HWHM}\simeq\Gamma/2.
\]

LOPC 的两个耗散通道由耦合模共同承担；模的衰减应由复频率零点决定，不能直接取 \(\Gamma+\gamma\)。FH 散射效率和仪器卷积又会改变强度曲线，因此 **\(\Gamma\)、\(\gamma\) 都不等于观测峰的 FWHM**。

很小的拟合 \(\Gamma\) 只表示模型中的晶格耗散很小。是否意味着材料本征寿命很长，还取决于仪器展宽、参数相关性及未建模响应；不能仅据此认定样品极其纯净。

### 5.3 强载流子阻尼下的组合参数

若整个窗口满足 \(\gamma\gg|\omega|\)，则：

\[
-\frac{\omega_p^2}{\omega(\omega+i\gamma)}
\simeq\frac{iK}{\omega},
\qquad K=\frac{\omega_p^2}{\gamma}.
\]

介电响应主要感受到 \(K\)，而非分别感受到 \(\omega_p\)、\(\gamma\)。在上述单载流子模型和 SI 角频率单位下：

\[
K=\frac{ne\mu}{\epsilon_0\epsilon_\infty}
=\frac{\sigma_{\mathrm{dc}}}{\epsilon_0\epsilon_\infty}.
\]

**\(K\)**：背景介电常数归一化的电导率尺度。它是强阻尼近似下的组合量，不能作为任意 FH 线型的严格不变量，也不能替代声子阻尼。不同参数组给出相似曲线，可能源于这种灵敏度退化，而非存在两种不同的材料状态。

### 5.4 强度、散射效率与仪器展宽

以屏蔽 \(\omega_p\) 为独立参数时，模型强度只包含比值 \(I_0/\epsilon_\infty\)。未引入独立约束的单条谱不能分别确定二者；\(\epsilon_\infty\) 的变化不能直接解释成电子极化变化，\(I_0\) 的变化也不能直接解释成散射强度变化。数学上的等价变换见数学文档第 8 节。

\(C\) 改变形变势与电光机制的干涉；总强度非负并不要求 \(C\ge0\)。若窗口内 \(A_{\mathrm{FH}}\) 近似常数，其作用主要被 \(I_0\) 吸收，此时 \(C\) 的反演也不敏感。

\[
\mathrm{FWHM}_G=2\sqrt{2\ln2}\,\sigma_{\mathrm{inst}}.
\]

自由拟合的 \(\sigma_{\mathrm{inst}}\) 与本征线宽可能相关；只有仪器标定支持时，才能将它单独解释为仪器分辨率。采样间隔也不等于仪器分辨率；远小于采样间隔的离散卷积宽度可能没有可辨识的曲线差异。

### 5.5 从曲线一致性到物理解释

残差小不保证参数唯一，也不单独确认 LOPC 或 Fano 机制。材料参数的解释需要同时满足：参数可辨识、结果对噪声和初值稳定、参考材料条件适用，并与独立电学或仪器信息相容。

LOPC 需区分载流子耦合、应变和温升造成的频移；Fano 需有兼容对称性通道的电子连续态及干涉证据。空间平均、角向色散和仪器响应可产生竞争解释，见附录 A。

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

基线算法只能估计预处理背景，不能替代电子连续态模型。仪器 Gaussian 展宽应对完整 LOPC 或 Fano 响应卷积，不能用基线或独立峰宽吸收真实的物理结构。Voigt 是参考模型，不应被当作 LOPC 或 Fano 的物理解释。

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
