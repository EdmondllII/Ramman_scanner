# GaN \(A_1(\mathrm{LO})\) LOPC 拟合函数

## 1. 频率变量

\[
\omega=2\pi c\,\widetilde\nu,
\qquad
x(\omega)=\frac{\omega-\omega_c}{\omega_c}.
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
-\omega^{2}\eta
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
+\omega_{\mathrm p}^{2}\eta
(\omega_{\mathrm p}^{2}-2\omega^{2})
+
\omega^{2}\eta(\omega^{2}+\gamma^{2})
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

将常数并入总幅度：

\[
\boxed{
I_{\mathrm{LOPC}}^{(\mathrm{Lor})}(\omega)
=
\widetilde I_0
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

\[
w_i=\frac{1}{s_i^2},
\qquad
\mathrm{RSS}
=
\sum_{i=1}^{N}
\left[
y_i-I_{\mathrm{fit}}(\omega_i;\boldsymbol\theta)
\right]^2.
\]

## 7. 参数展开

\[
\boldsymbol\theta_{\mathrm{fit}}
=
\left(
I_0,\omega_{\mathrm p},\Gamma,\gamma,C,\eta,
\sigma,\omega_c,\beta_0,\ldots,\beta_m
\right).
\]

\[
\boldsymbol\theta_{\mathrm{fixed}}
=
\left(
\omega_{\mathrm L},\omega_{\mathrm T},\epsilon_\infty
\right).
\]

\[
\boldsymbol\theta_{\mathrm{full}}
=
\left(
\boldsymbol\theta_{\mathrm{fit}},
\omega_{\mathrm L},\omega_{\mathrm T},\epsilon_\infty
\right).
\]

\[
\omega_{\mathrm p}^{2}
=
\frac{ne^{2}}
{\epsilon_0\epsilon_\infty m^*}
\quad\text{(SI)},
\qquad
\omega_{\mathrm p}^{2}
=
\frac{4\pi ne^{2}}
{\epsilon_\infty m^*}
\quad\text{(Gaussian--cgs)}.
\]

\[
I_0\ge0,\qquad
\omega_{\mathrm p}\ge0,\qquad
\Gamma>0,\qquad
\gamma>0,\qquad
\sigma\ge0.
\]
