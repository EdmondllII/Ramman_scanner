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

Adam 和 LM 不设人为参数上限，不将 `omega_l` 限制在数据窗口内；保留非负振幅和频率、阻尼、介电常数的物理正值要求。`omega_t` 和 `epsilon_inf` 默认固定，可用 `vary_omega_t`、`vary_epsilon_inf` 控制是否参与 LM 优化。

## run.py

```bash
python work/fitting/run.py
```

**用途与模型**：读取原始 TIFF 和背景 TIFF，相减后寻峰并进行多峰拟合。`FIT_METHOD` 默认为 Gaussian，默认处理全部空间点。

**输入、输出**：`INPUT_PATH` 默认 `input.tif`，`BACKGROUND_PATH` 默认 `work/baseline/output/background.tif`；在 `OUTPUT_DIR` 保存 `fit_parameters.csv`、`metadata.json`。参数表包含坐标、峰编号、峰位、峰高、面积、宽度和 FWHM，不含混合模型的 `model` 列。

**需要修改的配置**：顶部 `READ_DATA`、`FIT_METHOD`、`READER_OPTIONS`、`PEAK_OPTIONS`、`FIT_OPTIONS`。路径和范围也可通过 `--input`、`--background`、`--output`、`--y-start`、`--y-end`、`--x-start`、`--x-end` 覆盖，其中 `--output` 指定目录。输入应为原始谱，避免对已校正谱再次扣背景。
