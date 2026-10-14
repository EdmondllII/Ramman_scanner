# GaN \(A_1(\mathrm{LO})\) LOPC 拟合函数

本文给出 LOPC、FH 与 Gaussian 卷积的公式、符号、单位及可辨识性。参数的物理意义见《[载流子效应与线形模型](GaN_A1LO_载流子效应与线形模型.md)》；脚本选择和配置见 [fitting README](../../work/fitting/README.md)，具体拟合结果见 [reports](../reports/README.md)。

## 0. 参数符号与单位

以下频率类参数按 Raman 波数表示；若改用角频率，须按第 1 节统一转换。

**omega_p（\(\omega_p\)）**：\(\mathrm{cm^{-1}}\)。

**gamma_p（\(\gamma\)）**：\(\mathrm{cm^{-1}}\)。

**gamma_ph（\(\Gamma\)）**：\(\mathrm{cm^{-1}}\)。

**omega_l（\(\omega_L\)）**：\(\mathrm{cm^{-1}}\)。

**omega_t（\(\omega_T\)）**：\(\mathrm{cm^{-1}}\)。

**epsilon_inf（\(\epsilon_\infty\)）**：无量纲。

**amplitude（\(I_0\)）**：与观测强度 \(y\) 相同的单位，未标定时为 \(\mathrm{a.u.}\)；这是 LOPC／FH 的乘法系数，不是 \(\max I\)。

**C（\(C\)）**：无量纲。

**sigma_inst（\(\sigma=\sigma_{\mathrm{inst}}\)）**：\(\mathrm{cm^{-1}}\)；Gaussian 标准差。

辅助量：

**\(\omega_c\)**：\(\mathrm{cm^{-1}}\)；背景基函数的参考坐标。

**\(\beta_k\)**：与 \(y\) 相同的单位；第 5 节采用无量纲基函数 \(x^k\)。

**alpha（\(\alpha\)）**：无量纲；第 6 节的饱和权重增量。

**scale（\(s\)）**：与 \(y\) 相同的单位；饱和权重的强度尺度。

**\(s_i\)**：与 \(y\) 相同的单位；观测噪声标准差。

参考 Lorentzian／Fano 的符号见物理文档第 1.2、3 节：

**\(\omega_0\)、\(\kappa\)、\(\omega_F\)、\(\Gamma_F\)**：\(\mathrm{cm^{-1}}\)；\(\kappa\) 为 Lorentzian 半高半宽，\(\Gamma_F\) 为 Fano 分母中的宽度。

**\(q_F\)**：无量纲。

**\(I_c\)**：与 \(y\) 相同的单位。

**\(A\)、\(A_{\mathrm{Lor}}\)**：强度单位乘频率单位；乘以单位面积的参考线型或第 4.1 节的 Lorentzian 核。

材料反演采用 SI 角频率时，物理文档中的量使用：

**\(n\)**：\(\mathrm{m^{-3}}\)；换算为 \(\mathrm{cm^{-3}}\) 时数值乘 \(10^{-6}\)。

**\(m^*\)**：\(\mathrm{kg}\)；\(m^*/m_e\) 无量纲。

**\(\mu\)**：\(\mathrm{m^2\,V^{-1}\,s^{-1}}\)；换算为 \(\mathrm{cm^2\,V^{-1}\,s^{-1}}\) 时数值乘 \(10^4\)。

**\(\tau_p\)、\(\tau_{\mathrm{amplitude}}\)、\(\tau_{\mathrm{energy}}\)**：\(\mathrm s\)。

**\(\sigma_{\mathrm{dc}}\)**：\(\mathrm{S\,m^{-1}}\)。

**\(K=\omega_p^2/\gamma\)**：\(\mathrm{s^{-1}}\)；若全部采用波数，则为 \(\mathrm{cm^{-1}}\)。

\(\epsilon\)、\(\mathcal L\)、\(A_{\mathrm{FH}}\)、\(x\) 均无量纲；\(G_\sigma\) 的单位为频率单位的倒数，归一化卷积不改变强度单位。

## 1. 频率变量

\[
\omega=2\pi c\,\widetilde\nu,
\qquad
x(\omega)=\frac{\omega-\omega_c}{\omega_c}.
\]

第 2–5 节的线型可统一使用角频率或波数；\(\omega_p\)、\(\omega_L\)、\(\omega_T\)、\(\Gamma\)、\(\gamma\)、\(\sigma\) 必须与横轴同单位。若 \(\widetilde\nu\) 用 \(\mathrm{cm^{-1}}\)，则转换式中的 \(c\) 用 \(\mathrm{cm\,s^{-1}}\)。

例如阻尼的两种表示满足：

\[
\Gamma_{\mathrm{angular}}=2\pi c\,\widetilde\Gamma,
\qquad
\gamma_{\mathrm{angular}}=2\pi c\,\widetilde\gamma.
\]

## 2. 介电函数

\[
\epsilon(\omega)
=
\epsilon_{\infty}
\left[
1+
\frac{\omega_{\mathrm L}^{2}-\omega_{\mathrm T}^{2}}
{\omega_{\mathrm T}^{2}-\omega^{2}-i\omega\Gamma}
-
\frac{\omega_{\mathrm p}^{2}}
{\omega(\omega+i\gamma)}
\right].
\]

\[
\mathcal L(\omega)
=
\operatorname{Im}\left[-\frac{1}{\epsilon(\omega)}\right].
\]

## 3. Faust--Henry 因子

以下公式对应[原文](trnit1999_195-220.pdf)印刷页 197 的式 (3.2)、(3.3)、(3.5)。介电函数、\(\Delta\) 和 Faust–Henry 分子中的 \(\Gamma\) 是同一个参数；\(\Gamma=\texttt{gamma\_ph}\)，\(\gamma=\texttt{gamma\_p}\)。

\[
\Delta(\omega)
=
\omega_{\mathrm p}^{2}\gamma
\left[
(\omega_{\mathrm T}^{2}-\omega^{2})^{2}
+(\omega\Gamma)^{2}
\right]
+
\omega^{2}\Gamma
(\omega_{\mathrm L}^{2}-\omega_{\mathrm T}^{2})
(\omega^{2}+\gamma^{2}).
\]

\[
\begin{aligned}
A_{\mathrm{FH}}(\omega)
=\;&1
+\frac{2C\omega_{\mathrm T}^{2}}{\Delta(\omega)}
\Big[
\omega_{\mathrm p}^{2}\gamma
(\omega_{\mathrm T}^{2}-\omega^{2})
\\
&\qquad
-\omega^{2}\Gamma
(\omega^{2}+\gamma^{2}-\omega_{\mathrm p}^{2})
\Big]
\\
&+\frac{C^{2}\omega_{\mathrm T}^{4}}
{\Delta(\omega)(\omega_{\mathrm L}^{2}-\omega_{\mathrm T}^{2})}
\Big[
\omega_{\mathrm p}^{2}\gamma
(\omega_{\mathrm L}^{2}-\omega_{\mathrm T}^{2})
\\
&\qquad
+\omega_{\mathrm p}^{2}\Gamma
(\omega_{\mathrm p}^{2}-2\omega^{2})
+
\omega^{2}\Gamma(\omega^{2}+\gamma^{2})
\Big].
\end{aligned}
\]

## 4. 本征拟合函数

\[
S_{\mathrm{LOPC}}(\omega)
=
A_{\mathrm{FH}}(\omega)\mathcal L(\omega).
\]

\[
I_{\mathrm{LOPC}}^{(0)}(\omega)
=
I_0S_{\mathrm{LOPC}}(\omega).
\]

若在拟合窗口 \(\Omega\) 内：

\[
A_{\mathrm{FH}}(\omega)
=
A_0[1+\delta_A(\omega)],
\qquad
\sup_{\omega\in\Omega}|\delta_A(\omega)|\ll1,
\]

则：

\[
I_{\mathrm{LOPC}}^{(0)}(\omega)
\simeq
I_0A_0\mathcal L(\omega)
\equiv
\widetilde I_0\mathcal L(\omega).
\]

归一化 \(A_0=1\) 后：

\[
\boxed{
I_{\mathrm{LOPC}}^{(\mathrm{min})}(\omega)
=
\widetilde I_0
\operatorname{Im}\left[-\frac1{\epsilon(\omega)}\right]
}.
\]

若 \(A_{\mathrm{FH}}(\omega)\) 不满足上述条件，则保留：

\[
I_{\mathrm{LOPC}}^{(0)}(\omega)
=
I_0A_{\mathrm{FH}}(\omega)
\operatorname{Im}\left[-\frac1{\epsilon(\omega)}\right].
\]

### 4.1 Lorentzian 极限

无载流子极限 \(\omega_{\mathrm p}=0\) 下：

\[
\epsilon_0(\omega)
=
\epsilon_\infty
\frac{\omega_{\mathrm L}^{2}-\omega^{2}-i\omega\Gamma}
{\omega_{\mathrm T}^{2}-\omega^{2}-i\omega\Gamma}.
\]

\[
\mathcal L_0(\omega)
=
\operatorname{Im}\left[-\frac1{\epsilon_0(\omega)}\right]
=
\frac{
\Gamma\omega(\omega_{\mathrm L}^{2}-\omega_{\mathrm T}^{2})
}
{
\epsilon_\infty
\left[
(\omega_{\mathrm L}^{2}-\omega^{2})^{2}
+(\Gamma\omega)^{2}
\right]
}.
\]

若载流子项满足：

\[
\left|
\frac{\omega_{\mathrm p}^{2}}
{\omega(\omega+i\gamma)}
\right|
\ll1,
\]

并且在单个 LO 共振附近：

\[
|\omega-\omega_{\mathrm L}|\ll\omega_{\mathrm L},
\qquad
\Gamma\ll\omega_{\mathrm L},
\]

则：

\[
\omega_{\mathrm L}^{2}-\omega^{2}
\simeq
-2\omega_{\mathrm L}(\omega-\omega_{\mathrm L}),
\qquad
\omega\simeq\omega_{\mathrm L},
\]

\[
\mathcal L_0(\omega)
\simeq
\frac{\omega_{\mathrm L}^{2}-\omega_{\mathrm T}^{2}}
{2\epsilon_\infty\omega_{\mathrm L}}
\frac{\Gamma/2}
{(\omega-\omega_{\mathrm L})^{2}+(\Gamma/2)^{2}}.
\]

再取峰附近 \(A_{\mathrm{FH}}\simeq A_0\)，将常数并入 Lorentzian 系数：

\[
A_{\mathrm{Lor}}=
\widetilde I_0\frac{\omega_L^2-\omega_T^2}{2\epsilon_\infty\omega_L}.
\]

\[
\boxed{
I_{\mathrm{LOPC}}^{(\mathrm{Lor})}(\omega)
=
A_{\mathrm{Lor}}
\frac{\Gamma/2}
{(\omega-\omega_{\mathrm L})^{2}+(\Gamma/2)^{2}}
}.
\]

\[
\sigma>0
\quad\Longrightarrow\quad
I_{\mathrm{meas}}^{(\mathrm{Lor})}
=
G_\sigma*
I_{\mathrm{LOPC}}^{(\mathrm{Lor})}
\quad\text{（Voigt 形式）}.
\]

## 5. 仪器卷积与基线

\(\sigma=\sigma_{\mathrm{inst}}>0\) 时：

\[
G(\omega;\sigma)
=
\frac{1}{\sqrt{2\pi}\sigma}
\exp\left(-\frac{\omega^2}{2\sigma^2}\right).
\]

\[
(G_\sigma*S)(\omega)
=
\int_{-\infty}^{\infty}
G(\omega-\omega';\sigma)S(\omega')\,\mathrm d\omega'.
\]

\[
B_m(\omega)
=
\sum_{k=0}^{m}\beta_kx(\omega)^k.
\]

\[
I_{\mathrm{fit}}(\omega)
=
I_0(G_\sigma*S_{\mathrm{LOPC}})(\omega)
+B_m(\omega).
\]

\(B_m\equiv0\) 时得到不含背景项的线型。

\[
G(\omega;\sigma)
\xrightarrow[\sigma\to0]{}\delta(\omega),
\qquad
I_{\mathrm{fit}}(\omega)
=
I_0S_{\mathrm{LOPC}}(\omega)+B_m(\omega).
\]

## 6. 拟合目标

\[
\widehat{\boldsymbol\theta}
=
\underset{\boldsymbol\theta\in\Theta}{\operatorname{arg\,min}}
\sum_{i=1}^{N}
w_i
\left[
y_i-I_{\mathrm{fit}}(\omega_i;\boldsymbol\theta)
\right]^2.
\]

普通最小二乘取 \(w_i=1\)；已知独立噪声标准差 \(s_i\) 时，可取 \(w_i=1/s_i^2\)。按观测强度生成固定的饱和权重时：

\[
w_i=1+\alpha\left[1-\exp\left(-\frac{\max(y_i,0)}s\right)\right],
\qquad \alpha\ge0,\quad s>0.
\]

\[
1\le w_i<1+\alpha\quad(\alpha>0),
\qquad
\frac{\mathrm dw_i}{\mathrm dy_i}=\frac\alpha s e^{-y_i/s},
\quad
\frac{\mathrm d^2w_i}{\mathrm dy_i^2}=-\frac\alpha{s^2}e^{-y_i/s}
\quad(y_i>0).
\]

权重只由观测数据和预设 \(\alpha,s\) 决定，不随待拟合曲线变化，也不把 \(\alpha,s\) 加入线型参数。\(\alpha=0\) 恢复普通最小二乘。

优化器的残差乘数为 \(\sqrt{w_i}\)，与目标函数中的 \(w_i\) 区分：

\[
r_i=\sqrt{w_i}\,[y_i-I_{\mathrm{fit}}(\omega_i)],
\qquad Q=\sum_i r_i^2.
\]

未加权的评价量另记为：

\[
\mathrm{RSS}
=
\sum_{i=1}^{N}
\left[
y_i-I_{\mathrm{fit}}(\omega_i;\boldsymbol\theta)
\right]^2.
\]

## 7. 参数集合与定义域

\[
\boldsymbol\theta_{\mathrm{LOPC}}
=
\left(
I_0,\omega_{\mathrm p},\Gamma,\gamma,
\omega_{\mathrm L},\omega_{\mathrm T},\epsilon_\infty
\right).
\]

\[
\boldsymbol\theta_{\mathrm{FH}}=(\boldsymbol\theta_{\mathrm{LOPC}},C),
\qquad
\boldsymbol\theta_{\mathrm{FH+G}}=(\boldsymbol\theta_{\mathrm{FH}},\sigma).
\]

若包含背景，另加 \((\beta_0,\ldots,\beta_m)\)，\(\omega_c\ne0\) 为选定的基函数参考坐标。实际优化变量与固定量是模型参数的两个互补子集；公式不强制固定 \(\omega_L\)、\(\omega_T\) 或 \(\epsilon_\infty\)。

\[
I_0\ge0,\qquad \omega_p\ge0,\qquad
\Gamma>0,\qquad \gamma>0,\qquad \sigma\ge0,
\]

\[
\omega_L>\omega_T>0,\qquad
\epsilon_\infty>0,\qquad C\in\mathbb R.
\]

\(\sigma=0\) 按第 5 节的极限定义；\(\omega_p=0\) 时 \(\gamma\) 从介电函数和 FH 因子中消失。上述表达式在正频率窗口上使用，不直接代入 \(\omega=0\)。

## 8. 拟合结果的数学解释

### 8.1 峰位与宽度

\[
\omega_{\mathrm{peak}}=\underset{\omega\in\Omega}{\operatorname{arg\,max}}
[I_{\mathrm{fit}}(\omega)-B_m(\omega)].
\]

一般没有 \(\omega_{\mathrm{peak}}=\omega_L\) 或 \(I_{\mathrm{peak}}=I_0\)。若存在唯一峰顶及两侧半高交点，FWHM 为两交点的频率差；第 4.1 节的窄 Lorentzian 极限才有 \(\mathrm{FWHM}\simeq\Gamma\)。Gaussian 单独满足 \(\mathrm{FWHM}_G=2\sqrt{2\ln2}\,\sigma\)；卷积后的 FWHM 不是两种宽度的简单相加。

### 8.2 整体强度的精确退化

令 \(\epsilon=\epsilon_\infty F\)。以 \(\omega_p\) 为独立参数时，\(F\) 与 \(A_{\mathrm{FH}}\) 都不含 \(\epsilon_\infty\)，于是：

\[
I_{\mathrm{fit}}-B_m
=\frac{I_0}{\epsilon_\infty}
\left[G_\sigma*
\left(A_{\mathrm{FH}}\operatorname{Im}\left[-\frac1F\right]\right)\right].
\]

\[
(I_0,\epsilon_\infty)\mapsto(aI_0,a\epsilon_\infty),
\qquad a>0
\quad\Longrightarrow\quad I_{\mathrm{fit}}\text{ 不变}.
\]

因此该线型只能识别 \(I_0/\epsilon_\infty\)，不能独立识别两者。两者同时自由变化时，Jacobian 的对应列线性相关，\(J^TWJ\) 奇异；分别报告有限的局部标准误差没有依据。

这里 \(J_{ij}=\partial I_{\mathrm{fit}}(\omega_i)/\partial\theta_j\)，\(W=\operatorname{diag}(w_i)\)。近似线性相关也会使参数估计对噪声和初值敏感。

### 8.3 近似退化与采样

强阻尼窗口中的展开为：

\[
-\frac{\omega_p^2}{\omega(\omega+i\gamma)}
=\frac{i\omega_p^2}{\gamma\omega}
-\frac{\omega_p^2}{\gamma^2}
+O\!\left(\frac{\omega_p^2|\omega|}{\gamma^3}\right),
\qquad |\omega|/\gamma\ll1.
\]

首项仅含 \(\omega_p^2/\gamma\)；高阶项或其他因子不足以区分参数时，可出现近似等价解。这不是任意 FH 参数组都具有相同组合量的证明。

等间隔 \(\Delta\omega\) 的离散 Gaussian 核满足：

\[
\frac{g_{\pm1}}{g_0}
=\exp\left[-\frac{(\Delta\omega)^2}{2\sigma^2}\right]
\xrightarrow[\sigma/\Delta\omega\to0]{}0.
\]

此时离散卷积趋于恒等映射；多个很小的 \(\sigma\) 可给出数值上相同的曲线。残差相近只说明输出曲线接近，不保证每个拟合参数都被数据独立确定。
