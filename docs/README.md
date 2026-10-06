# 项目文档

这里记录项目的设计、工作流、数据约定、数学与物理原理，以及阶段性研究结论。

代码目录中的 README 主要说明“怎么使用”；本目录主要说明“为什么这样设计、各步骤如何衔接、模型代表什么以及当前结论有什么边界”。具体脚本用法请回到 [`raman/README.md`](../raman/README.md)、[`work/README.md`](../work/README.md) 及其子目录 README。

## 从哪里开始

1. 先看[项目结构与工作流](architecture/workflow_design.md)，了解 `raman/` 和 `work/` 的职责边界。
2. 再看[数据与结果约定](architecture/data_contract.md)，了解 TIFF、CSV、参数表和坐标之间的关系。
3. 再看[物理模型与当前拟合](models/GaN_A1LO_载流子效应与线形模型.md)，了解当前 LOPC/Fano 讨论和解释限制。
4. 需要理解具体算法时，查看[模型公式](models/GaN_A1LO_拟合数学模型.md)以及[依赖库原理调研](research/README.md)。
5. 需要了解开发过程和历史背景时，查看[实施计划](plans/Adam预优化_LM实施计划.md)和[阶段报告](reports/README.md)。

## 文档分区

### 架构与流程

- [项目结构与工作流](architecture/workflow_design.md)：代码分层、处理顺序、输入输出关系。
- [数据与结果约定](architecture/data_contract.md)：光谱轴、扫描立方体、参数表和结果文件关系。

### 模型与物理

- [GaN A1(LO) 载流子效应专题](models/GaN_A1LO_载流子效应与线形模型.md)：LOPC、Fano 及物理解释边界。
- [GaN A1(LO) LOPC 拟合函数](models/GaN_A1LO_拟合数学模型.md)：拟合函数、参数和目标函数。

### 依赖库原理

- [lmfit-py 数学与物理原理调研](research/lmfit-py_数学与物理原理调研.md)
- [pybaselines 数学与物理原理调研](research/pybaselines_数学与物理原理调研.md)
- [RamanSPy 数学与物理原理调研](research/RamanSPy_数学与物理原理调研.md)
- [依赖库调研说明](research/README.md)

### 开发计划

- [Adam 预优化与 LM 精修实施计划](plans/Adam预优化_LM实施计划.md)

### 阶段记录

- [阶段记录索引](reports/README.md)：组会周报、拟合评估、峰归因与振幅物理约束分析。
- [2026-09-21 组会周报](reports/组会周报_2026-09-21.md)

HTML 文件是周报的导出版本；Markdown 是可编辑的源文件。

## 代码与文档的边界

| 内容 | 主要位置 |
| --- | --- |
| 单条光谱读取、基线、拟合、重建算法 | `raman/` |
| 扫描遍历、结果保存、评估和绘图脚本 | `work/` |
| 流程设计、数据关系、数学和物理解释 | `docs/` |
| 脚本参数、命令和具体使用方法 | 各目录 README |

研究文档可以引用代码和 README，但不重复维护脚本参数表；代码行为发生变化时，应优先更新对应 README，再检查本目录中的设计和模型说明是否仍然成立。
