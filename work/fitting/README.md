# 峰检测与拟合

本目录逐空间点检测候选峰并拟合。当前 LOPC 探索使用 `fit_scan.py`；`run.py` 是原有 Gaussian 工作流。所有命令在项目根目录执行。

两条路径均只保留高度严格大于零的候选峰，拟合振幅设非负下界；拟合后高度小于等于零的分量不写入参数表，原峰编号保留。输入校正谱中的负值不会被截断。

## fit_scan.py

```bash
python work/fitting/fit_scan.py
```

**用途与模型**：读取已扣背景的光谱。在 `LOPC_RANGE`（默认 720–750 cm⁻¹）内恰好检测到一个候选峰时，对该窗口使用 LOPC，其余峰使用 Lorentzian；窗口内没有候选峰或有多个候选峰时不启用 LOPC。TIFF 每点独立拟合，不求平均谱。

**输入、输出**：`INPUT_PATH` 默认 `work/baseline/output/corrected.tif`，也支持两列 CSV；CSV 按 `(x=0, y=0)` 处理。`OUTPUT_PATH` 默认 `work/fitting/output/fit_parameters_lopc.csv`。

参数表通过 `model` 列区分 `lorentzian` 和 `lopc`。Lorentzian 行使用 `position`、`height`、`amplitude`、`sigma`、`fwhm`；LOPC 行使用 `position`、`height`、`amplitude`、`omega_l`、`omega_p`、`gamma_p`、`gamma_ph`、`omega_t`、`epsilon_inf`。不适用列为 `NaN`；LOPC 的 `position` 是窗口内拟合曲线的离散最大值位置，不等同于 `omega_l`。

**需要修改的配置**：顶部路径、`READER_OPTIONS`、`PEAK_OPTIONS`（寻峰）、`FIT_OPTIONS`（Lorentzian）、`LOPC_RANGE`（候选峰和数据分区）、`LOPC_OPTIONS`（LOPC 初值、材料参数和优化器）。`Y_START/Y_END`、`X_START/X_END` 控制空间范围，默认只处理 `(x=0, y=0)`。

`LOPC_OPTIONS["optimizer"]` 当前为 `"adam_then_lm"`，先由 PyTorch Adam 搜索初值区域，再由 lmfit `leastsq`/LM 精修。`adam_options` 控制学习率、步数、早停和种子；改为 `"lm"` 可关闭预优化。Torch 通过 `D:\Edmon\Miniconda\envs\env1\Lib\site-packages` 导入，导入或运行阶段失败时回退到原始初值执行 LM。

`WEIGHT_OPTIONS` 控制加权最小二乘，当前启用，实验初值为 `alpha=6.0`、`scale=3.0`。平方误差权重为 `w=1+alpha*(1-exp(-max(y,0)/scale))`，只由观测数据计算一次；`scale` 是强度单位，控制饱和速度，`alpha` 控制最大额外权重。当前权重从 1 增长至 7，负值和零值权重为 1。Lorentzian、LOPC 的 Adam 和 LM 均使用固定的 `sqrt(w)` 残差乘数。设置 `enabled=False` 恢复普通最小二乘；不影响寻峰或参数约束。评估脚本仍报告未加权误差，便于对照；加权拟合的参数不确定度不能直接解释为测量误差。

Adam 和 LM 不设人为参数上限，不将 `omega_l` 限制在数据窗口内；保留非负振幅和频率、阻尼、介电常数的物理正值要求。`omega_t` 和 `epsilon_inf` 默认固定，可用 `vary_omega_t`、`vary_epsilon_inf` 控制是否参与 LM 优化。

## fit_scan_fh.py

```bash
python work/fitting/fit_scan_fh.py
```

**用途与模型**：从 `fit_scan.py` 复制的独立完整 A 项实验。LOPC 区间使用 `I0 * A_FH(ω) * Im[-1/ε(ω)]`，其余峰继续使用 Lorentzian；寻峰、数据分区和加权规则与复制时的配置一致。拟合接口为 `raman/fitting/lopc_fh.py`，独立 Adam 为 `adam_prefit_fh.py`；拟合、重建与 Torch 共用 `raman/lineshapes.py` 的完整代数公式。

**输入、输出**：共用 `work/baseline/output/corrected.tif`，也支持 CSV；输出 `work/fitting/output/fit_parameters_lopc_fh.csv`。完整 A 项行标记为 `model=lopc_fh`，新增 `C` 列；Lorentzian 行的 `C` 为 NaN。必须使用对应的 `reconstruct_spectrum_fh.py` 重建。

**需要修改的配置**：顶部路径、寻峰、加权、LOPC 区间及优化器配置与旧脚本相同，单独维护。`LOPC_OPTIONS["C"]=0.0` 是初值，`vary_C=True` 时 Adam 和 LM 均优化 C。C 有符号、无量纲，不设上下限；0 对应常数散射因子的旧模型。未采用文献的固定 C=0.55。振幅非负，频率和阻尼保持物理正值，LO 频率通过正的 LO–TO 间隔保持高于 TO；不设人为频率窗口或上限。`vary_C=False` 可做固定 C 对照。`WEIGHT_OPTIONS["enabled"]=False` 恢复不加权。

公式依据 [原文](../../docs/models/trnit1999_195-220.pdf) 印刷页 197 式 (3.2)–(3.3)：声子阻尼统一为 `gamma_ph`，二次 C 项保留 `omega_p² * gamma_ph * (omega_p² - 2ω²)`。旧数学文档中的未定义 `η` 和漏写因子未照搬。该实验未加入 B 散射项、仪器卷积或局部背景；增加 C 不保证解决参数退化，应比较残差和参数稳定性。

## run.py

```bash
python work/fitting/run.py
```

**用途与模型**：读取 baseline 已生成的校正 TIFF，直接寻峰并进行多峰拟合，不读取背景或重复扣除。`FIT_METHOD` 默认为 Gaussian，默认处理全部空间点。

**输入、输出**：`INPUT_PATH` 默认 `work/baseline/output/corrected.tif`；在 `OUTPUT_DIR` 保存 `fit_parameters.csv`、`metadata.json`。参数表包含坐标、峰编号、峰位、峰高、面积、宽度和 FWHM，不含混合模型的 `model` 列。

**需要修改的配置**：顶部 `READ_DATA`、`FIT_METHOD`、`READER_OPTIONS`、`PEAK_OPTIONS`、`FIT_OPTIONS`。路径和范围也可通过 `--input`、`--output`、`--y-start`、`--y-end`、`--x-start`、`--x-end` 覆盖，其中 `--input` 必须是已校正谱，`--output` 指定目录。旧 `--background` 参数已移除，先运行 baseline 步骤。

## fit_scan_fh_convolved.py

```bash
python work/fitting/fit_scan_fh_convolved.py
```

**用途与模型**：独立的 Gaussian 仪器卷积完整 A 项实验。LOPC 窗口使用
`I0 * G_sigma * [A_FH(ω) * Im(-1/epsilon(ω))]`，其他峰继续使用 Lorentzian；输入、寻峰、分区和权重规则与 `fit_scan_fh.py` 独立维护。`sigma_inst` 是固定 Gaussian 标准差，默认 1.0 cm⁻¹；新路径当前直接使用 LM，不调用未卷积的 Adam 预优化。

**输入、输出**：读取 `work/baseline/output/corrected.tif`，输出 `work/fitting/output/fit_parameters_lopc_fh_convolved.csv`。卷积 LOPC 行标记为 `model=lopc_fh_convolved`，并保存 `sigma_inst`。

**需要修改的配置**：顶部输入输出路径、`LOPC_RANGE`、`WEIGHT_OPTIONS`、`LOPC_OPTIONS` 和 `LOPC_OPTIONS["sigma_inst"]`。应优先把 `sigma_inst` 改成由仪器或标准样品标定的值；采样间隔不能直接当作仪器分辨率。模型公式见 [GaN A1LO 数学模型](../../docs/models/GaN_A1LO_拟合数学模型.md)第 5 节和 [完整 A 项工作流报告](../../docs/reports/LOPC_FH_拟合稳定性检查_2026-10-07.md)。
