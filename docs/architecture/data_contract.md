# 数据与结果约定

本文只记录各步骤之间必须保持一致的数据关系。具体路径和参数仍以 `work/` 中的脚本及其 README 为准。

## 光谱轴与扫描立方体

- 单条光谱由两列组成：`raman_shift` 和 `intensity`。
- 扫描 TIFF 统一按 `(y, x, Raman shift)` 使用，最后一维是光谱轴。
- 光谱之间进行比较、相加、相减或拟合前，Raman shift 轴必须逐点一致；代码不会替用户自动插值。
- `x`、`y` 是空间坐标，脚本中的扫描范围使用 Python 的左闭右开区间。

## 工作流中的文件

```text
原始 TIFF
   └─ baseline_scan.py
      ├─ background.tif
      ├─ corrected.tif
      └─ baseline/output/ 指定点校正 CSV
          └─ fit_scan.py
             └─ fit_parameters_lopc.csv
                 └─ reconstruct_spectrum.py
                    └─ reconstructed.csv
```

评估脚本只读取目标光谱和 reconstruction 已生成的拟合光谱，两条 CSV 位移轴必须一致；不读取参数、不重建、不拟合、不做物理归因，输出误差指标和残差。当前目标光谱是 baseline 已生成的校正谱。

可视化脚本只读取已有数据和结果并绘图，不扣背景、不重建、不计算评估指标。单谱展示读取已有原始、背景和校正文件；参数热力图只展示明确选择的峰，不对不同峰作统计聚合。基线处理及校正数据输出属于 baseline，从参数生成光谱属于 reconstruction；物理解释和归因记录属于 docs。

`raman/` 是算法库：`io/` 只读取文件，其余算法只处理内存数据并返回数组、数据对象或算法结果；不读取工作流文件、不创建工作流输出、不处理扫描空间循环。所有 CSV、TIFF、JSON、TXT 和 PNG 输出由 `work/` 入口负责。

## 参数表

拟合参数表是逐空间点、逐峰的长表。普通 Lorentzian 行和 LOPC 行通过 `model` 列区分；不适用的模型参数可以为空或为 `NaN`。重建时必须使用与 `model` 对应的参数列，不能把 LOPC 的 `omega_l` 直接当作观测曲线最大值位置。

## 维护规则

如果脚本的文件名、列名、轴顺序或输出格式发生变化，应同时检查：

1. 对应的 `work/*/README.md`；
2. 本文的流程图和字段说明；
3. [`docs/README.md`](../README.md) 中的导航链接。
