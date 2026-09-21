# 当前拟合效果评估与 GaN LED 峰归因

## 1. 评估对象

本次评估使用当前已经生成的结果，不重新执行基线校正，也不修改原有拟合器：

- 光谱：`work/baseline/output/corrected.tif`
- 参数表：`work/fitting/output/fit_parameters_lopc.csv`
- 空间点：`(x=0, y=0)`
- LOPC 窗口：`720--750 cm^-1`
- 本次参数表生成时的寻峰突出度系数：`0.025`（当前源码中的动态范围比例）

执行命令：

```powershell
D:\Edmon\Miniconda\envs\Raman\python.exe .\work\evaluation\evaluate_current_fit.py
```

输出位于 `work/evaluation/output/`：

- `fit_metrics_x0_y0.json`：数值指标和诊断项；
- `fit_spectrum_x0_y0.csv`：原始校正谱、总重建谱、两个模型分量和残差；
- `fit_report_x0_y0.txt`：简短文本报告。

## 2. 指标如何解释

脚本调用 `lmfit.minimizer.reduce_chisquare` 计算

\[
\chi^2=\sum_i(y_i-\hat y_i)^2,
\]

并按 lmfit 的定义重算 `redchi`、AIC、BIC 和 `R-squared`。这不是再次优化参数，而是对参数表中已经保存的参数进行重建和残差评价。

必须区分三个指标区域：

1. **全谱重建**：把全部 Lorentzian 和 LOPC 分量相加后与校正谱比较；它反映最终画出来的总曲线是否接近数据。
2. **Lorentzian 实际目标区间**：排除 `720--750 cm^-1` 后，只比较 Lorentzian 总和。`fit_scan.py` 的 Lorentzian 拟合就是在这个区间上执行的。
3. **LOPC 实际目标区间**：只比较 `720--750 cm^-1` 内的 LOPC 分量。当前 LOPC 拟合没有局部常数背景，因此这个指标也会暴露背景建模不足。

当前参数表只保存了最终参数，没有保存 lmfit 的 `ModelResult`。因此无法从 CSV 恢复原始的 `covar`、`nfev`、`success`、雅可比矩阵或原始 `fit_report()`。本评估中的 AIC/BIC 和 `redchi` 是按照 lmfit 公式用当前残差重算的诊断量，不应冒充原始优化器报告。

## 3. 当前结果的数值结论

运行脚本后应以 `fit_metrics_x0_y0.json` 为准。当前参数表对应的模型结构为：

- 8 个 Lorentzian；
- 1 个 LOPC；
- 按自由参数数量估算为 `8×3+1×5=29` 个参数；
- LOPC 参数大致为 `omega_l≈734.60 cm^-1`、`omega_p≈354.65 cm^-1`、`gamma_p≈3268.52 cm^-1`、`gamma_ph≈2.52×10^-5 cm^-1`。

本次实际运行得到的主要指标如下（残差是校正谱减重建谱）：

| 评估对象 | `chisqr` | `redchi` | RMSE | `R-squared` |
| --- | ---: | ---: | ---: | ---: |
| 全谱总重建 | 1407.57 | 0.958 | 0.969 | 0.9969 |
| Lorentzian 实际目标区间（排除 LOPC 窗口） | 953.94 | 0.694 | 0.826 | 0.9979 |
| LOPC 单独目标区间（仅 `720--750 cm^-1`） | 55.41 | 0.583 | 0.744 | 0.8407 |
| 所有分量相加后在 LOPC 窗口 | 305.20 | 4.299 | 1.747 | 0.1223 |

最后一行尤其重要：LOPC 本身在它的局部目标上并不算完全失配，但把在窗口外拟合出的宽 Lorentzian 也延拓并相加后，LOPC 窗口的总曲线明显变差。因此当前 `fit_scan.py` 的两个局部拟合结果不能直接当成一个在全谱上联合优化过的模型；全谱高 `R-squared` 也不能掩盖局部模型冲突。

这些数值说明 LOPC 在当前窗口内可以生成一个接近峰形的曲线，但不能把 `omega_p`、`gamma_p` 和 `gamma_ph` 直接当成可信的材料参数。`gamma_p` 远大于 30 cm^-1 的拟合窗口宽度，而 `gamma_ph` 远小于约 `0.30 cm^-1` 的采样间隔，属于明显的数值退化信号。

Lorentzian 参数也有同样的诊断问题：当前结果包含负振幅和很宽的分量，例如某些 `sigma` 远大于普通窄峰宽度。负振幅、相邻重复分量和超宽分量可以互相抵消，降低残差，却不等于发现了对应的物理振动模式。

因此，当前结果可以用于：

- 画出“数据与当前模型”的对比；
- 比较不同 `prominence` 或优化设置下的残差；
- 找出需要加边界、背景项或重新分区拟合的地方。

当前结果不能单独用于：

- 反演载流子浓度、迁移率或声子寿命；
- 证明存在 8 个独立的 GaN 声子；
- 仅凭 AIC/BIC 选择物理模型。

## 4. GaN 基 LED 的常见候选峰

下表给出在纤锌矿 GaN 及其 LED 外延结构中优先检查的候选区间。峰位会受到应变、温度、晶向、偏振、掺杂、激发波长和仪器标定影响，因此这里使用“候选”而不是硬编码的精确归属。

| 本次拟合位置/区间 | 常见候选归因 | 对当前结果的判断 |
| --- | --- | --- |
| `约 531--535 cm^-1` | GaN `A1(TO)` | 当前表中 `529.64 cm^-1` 可作为邻近候选，但偏离和线宽需要结合应变、温度及标定检查。 |
| `约 556--562 cm^-1` | GaN `E1(TO)`，是否可见强烈依赖晶向和偏振几何 | 当前参数表没有稳定落在该区间的独立峰，不能据此断言不存在。 |
| `约 564--570 cm^-1` | GaN `E2(high)`，通常是高质量 GaN 中最重要的强峰之一 | 当前 `567.84 cm^-1` 与该候选相符；但同时出现 `570.85 cm^-1` 和很宽的其它分量，说明多峰拟合可能在分摊一个主峰。 |
| `约 720--750 cm^-1` | GaN `A1(LO)`，在有自由载流子时表现为 LO-等离激元耦合（LOPC） | 当前 LOPC 曲线峰位 `736.57 cm^-1`、`omega_l≈734.60 cm^-1` 与该候选区间相符；这支持“使用 LOPC 作为候选线型”，不支持直接接受极端阻尼参数。 |
| `约 739--746 cm^-1` | GaN `E1(LO)` 候选，是否出现取决于晶向、偏振和选择定则 | 当前峰位没有足够证据区分 `A1(LO)` 与 `E1(LO)`；不能把 LOPC 模型标签当作对称性鉴定。 |
| `约 415 cm^-1` | 可能来自衬底、外延层/缺陷相关背景或仪器残留，不能仅凭 GaN 主声子表归因 | 当前 `415.27 cm^-1` 不应直接标为 GaN 基本允许声子。若 LED 使用蓝宝石衬底，应把衬底 Raman 参考谱纳入比较。 |
| `约 510--520 cm^-1`、`580--590 cm^-1`、`>750 cm^-1` | 可能是衬底峰、应变/缺陷相关结构、未分辨峰或过拟合分量 | 当前 `510.02`、`515.61`、`585.11`、`752.37 cm^-1` 的宽度/负振幅异常，暂不能给出唯一物理归因。 |

GaN LED 的 Raman 信号可能同时来自 p-GaN、量子阱、n-GaN、AlGaN、缓冲层和衬底。即使某个位置落在文献常见峰附近，也还需要偏振几何、层结构、应变/温度信息或对照样品来确认来源。特别是 `A1(LO)` 和 `E1(LO)` 的区分不能只靠一个无偏振峰位完成。

## 5. 推荐的归因顺序

1. 先用 `E2(high)` 附近的主峰检查位移标定、应变和温度趋势。
2. 再检查 `A1(TO)` 是否真的存在，以及它与 `E2(high)` 的相对强度是否符合测量偏振几何。
3. 对 `720--750 cm^-1` 只做“LO/LOPC 候选”标记；比较不同空间点或不同掺杂样品中的峰位、分裂和线宽变化。
4. 对 `415`、`510--520`、`580--590` 和 `750 cm^-1` 以上的结构，先测量/引入实际衬底参考谱，再考虑缺陷或第二相。
5. 在物理归因前，重新限制 Lorentzian 振幅为非负、给 `sigma` 设置合理上下界，并为 LOPC 窗口加入局部背景；否则优化器产生的补偿分量会污染归因。

## 6. 参考文献与适用边界

项目已有的专题文档 [`docs/GaN_A1LO_载流子效应与线形模型.md`](../../docs/GaN_A1LO_载流子效应与线形模型.md) 汇总了以下原始研究：

- Davydov et al., *Phonon dispersion and Raman scattering in hexagonal GaN and AlN*, Phys. Rev. B 58, 12899 (1998), [DOI: 10.1103/PhysRevB.58.12899](https://doi.org/10.1103/PhysRevB.58.12899)。该工作可作为纤锌矿 GaN 基本声子模式和频率范围的参考。
- Kozawa et al., *Raman scattering from LO phonon-plasmon coupled modes in gallium nitride*, J. Appl. Phys. 75, 1098 (1994), [DOI: 10.1063/1.356492](https://doi.org/10.1063/1.356492)。
- Demangeot et al., *Interplay of electrons and phonons in heavily doped GaN epilayers*, J. Appl. Phys. 82, 1305 (1997), [DOI: 10.1063/1.365903](https://doi.org/10.1063/1.365903)。
- Wieser et al., *Raman studies of longitudinal optical phonon-plasmon coupling in GaN layers*, J. Cryst. Growth 189--190, 661 (1998), [DOI: 10.1016/S0022-0248(98)00242-5](https://doi.org/10.1016/S0022-0248(98)00242-5)。
- Shi, Ponce and Menéndez, *Raman line shape of the A1 longitudinal optical phonon in GaN*, Appl. Phys. Lett. 84, 3471 (2004), [DOI: 10.1063/1.1737792](https://doi.org/10.1063/1.1737792)。

这些文献支持 GaN 中 LO-载流子耦合和复杂 LO 线形的存在，但不会自动证明当前每一个拟合分量都对应某一种材料机制。当前数据的可靠归因仍取决于原始层结构、衬底、偏振、激发条件和重复测量。
