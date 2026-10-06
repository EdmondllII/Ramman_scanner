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
      └─ 指定点校正 CSV
          └─ fit_scan.py
             └─ fit_parameters_lopc.csv
                 └─ reconstruct_spectrum.py
                    └─ reconstructed.csv
```

评估脚本读取校正光谱和拟合参数，输出 JSON 指标以及用于复核的残差 CSV；可视化脚本只读取已有结果，不改变数据。

## 参数表

拟合参数表是逐空间点、逐峰的长表。普通 Lorentzian 行和 LOPC 行通过 `model` 列区分；不适用的模型参数可以为空或为 `NaN`。重建时必须使用与 `model` 对应的参数列，不能把 LOPC 的 `omega_l` 直接当作观测曲线最大值位置。

## 维护规则

如果脚本的文件名、列名、轴顺序或输出格式发生变化，应同时检查：

1. 对应的 `work/*/README.md`；
2. 本文的流程图和字段说明；
3. [`docs/README.md`](../README.md) 中的导航链接。

