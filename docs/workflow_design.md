# 拉曼扫描数据工作流程设计

本文档规定项目后续的工作目录结构、脚本职责、中间结果格式和各步骤之间的衔接方式。

## 一、总体结构

项目不再依赖一个负责全部流程的 `main.py`。具体分析流程放在 `work/` 目录中，由用户根据需要单独运行某个步骤。

```text
Ramman_scanner/
├── raman/
│   ├── data.py
│   ├── io/
│   ├── baseline/
│   ├── fitting/
│   └── reconstruction/
│
├── work/
│   ├── baseline/
│   ├── fitting/
│   ├── reconstruction/
│   └── visualization/
│
├── docs/
├── requirements.txt
└── README.md
```

目录职责：

- `raman/`：存放可复用的算法、数据结构和读写接口。
- `work/`：存放面向实际分析的工作脚本，以及各步骤产生的结果。
- `docs/`：存放项目设计和使用说明。

`work/` 下的四个子目录分别对应四类工作，不要求按照单一固定流程全部执行。

## 二、`work/baseline/`

该目录负责对扫描数据中的每条谱线进行基线估计。

目录安排：

```text
work/baseline/
├── README.md
├── run.py
└── output/
    ├── background.tif
    └── metadata.json
```

`run.py` 的职责：

- 读取 TIFF 光谱立方体。
- 使用二重循环遍历空间点 `(y, x)`。
- 每次取出一个空间点的一维谱线。
- 调用 `raman/baseline/` 中选定的基线方法。
- 允许手动修改两个 `for` 循环的范围。
- 将每个空间点估计出的背景保存到结果立方体。

循环范围可以用于选择单点、局部区域或完整扫描区域。例如：

```python
for y_index in range(y_start, y_end):
    for x_index in range(x_start, x_end):
        ...
```

该步骤输出的是需要从原始谱线中扣除的背景部分，包括基线、荧光背景等：

```text
background = 原始光谱中需要扣除的部分
```

该步骤不输出基线扣除后的光谱。扣除后的光谱可以在后续步骤中根据原始光谱和 `background.tif` 得到：

```text
corrected = raw - background
```

输出文件：

- `background.tif`：形状为 `(y, x, Raman shift)` 的背景立方体。
- `metadata.json`：记录维度顺序、Raman 位移范围、数据类型、处理范围和基线方法及参数。

## 三、`work/fitting/`

该目录负责对扫描数据中的每条谱线进行峰检测和线形拟合。

目录安排：

```text
work/fitting/
├── README.md
├── run.py
└── output/
    ├── fit_parameters.csv
    └── metadata.json
```

`run.py` 的职责：

- 读取原始光谱和 `work/baseline/` 输出的背景数据。
- 用原始光谱减去背景，得到当前空间点的校正光谱。
- 使用与基线步骤相同的二重循环遍历空间点。
- 允许手动修改 `for` 循环范围，从而选择单点、局部区域或完整扫描区域。
- 对每个空间点单独进行峰检测和拟合。
- 只保存拟合参数，不保存拟合曲线数组。

拟合脚本不负责多个空间点之间的平均，也不使用平均谱线代替单点谱线。

输出参数采用长表形式，每行表示一个空间点的一个峰：

```text
x, y, peak_id, parameter_1, parameter_2, ...
```

建议至少包含以下字段：

- `x`：空间点的 x 坐标或 x 索引。
- `y`：空间点的 y 坐标或 y 索引。
- `peak_id`：该空间点中峰的编号。
- `position`：峰位置。
- `height`：峰高。
- `amplitude`：峰面积参数或振幅参数。
- `sigma`：线形宽度参数。
- `fwhm`：半高宽。

输出文件：

- `fit_parameters.csv`：逐空间点、逐峰保存的拟合参数。
- `metadata.json`：记录拟合方法、参数、处理范围、输入背景文件和输出字段说明。

## 四、`work/reconstruction/`

该目录包含多个彼此独立的重建或谱线运算脚本。每个脚本只完成一种操作，不负责重新拟合。

目录安排示例：

```text
work/reconstruction/
├── README.md
├── reconstruct_from_parameters.py
├── add_spectra.py
├── subtract_spectra.py
└── output/
```

脚本职责：

- `reconstruct_from_parameters.py`：根据拟合参数重建单条谱线、单个峰、多个分峰或总拟合谱。
- `add_spectra.py`：对指定谱线或重建谱线进行叠加。
- `subtract_spectra.py`：对指定谱线执行相减或背景扣除。

后续可以根据实际需要增加其他单一用途脚本，例如只重建某一个峰，或只计算两个组分的差谱。

重建脚本的输入主要是：

- `fit_parameters.csv`：拟合参数。
- Raman 位移坐标。
- 用户指定的峰编号、谱线坐标或模型参数。

重建脚本的输出可以是：

- 单个分峰的 CSV 光谱。
- 多个分峰组成的总拟合谱 CSV。
- 用于后续叠加或相减的中间谱线文件。

重建步骤不应修改拟合参数，也不应重新调用基线矫正或拟合算法。

## 五、`work/visualization/`

该目录包含多个只负责绘图的脚本。可视化脚本只读取已有结果，不负责重建，也不重新执行基线矫正和拟合。

目录安排示例：

```text
work/visualization/
├── README.md
├── plot_single_spectrum.py
├── plot_spectra_comparison.py
├── plot_parameter_heatmap.py
└── output/
```

脚本职责：

- `plot_single_spectrum.py`：绘制单个空间点的原始谱线、背景和校正谱线。
- `plot_spectra_comparison.py`：将多个空间点或多个输入文件的谱线放在同一张图中比较。
- `plot_parameter_heatmap.py`：读取逐点拟合参数，绘制指定参数的扫描空间热力图。

可视化脚本的输入可以是：

- 原始 TIFF 光谱立方体。
- `background.tif`。
- `fit_parameters.csv`。
- 重建目录中已经生成的 CSV 谱线。

可视化脚本的输出为 PNG、PDF 或其他图片文件，保存到当前脚本目录下的 `output/`。

热力图绘制时需要用户指定参数名，例如：

```text
position
height
amplitude
sigma
fwhm
```

脚本根据参数表中的 `x`、`y` 和目标参数值，将长表还原为空间分布后绘图。

## 六、算法包与工作脚本的边界

`raman/` 中的算法只处理一条谱线，不负责扫描区域遍历：

```python
corrected, background = airpls(x, intensity, ...)
fit_result = gaussian(x, corrected, centers=centers, ...)
```

`work/` 中的脚本负责：

- 选择输入文件。
- 选择具体算法。
- 设置参数。
- 设置空间点循环范围。
- 读取和保存中间结果。
- 调用单谱接口完成当前工作步骤。

这样可以保证算法实现保持简单，同时让每一个实验步骤都能单独运行、检查和重复。

## 七、结果格式约定

扫描数据统一使用以下维度顺序：

```text
(y, x, Raman shift)
```

建议的文件格式：

- TIFF：保存原始扫描数据或背景立方体。
- CSV：保存单条谱线、逐点拟合参数和重建谱线。
- JSON：保存维度、坐标、参数、方法名和处理范围等元数据。
- PNG 或 PDF：保存可视化结果。

每个 `work/` 子目录应将本步骤生成的结果放入自己的 `output/`，并通过 `metadata.json` 记录输入来源和处理配置，避免不同步骤之间的结果含义混淆。

## 八、参数列映射与线型选择

### 参数列映射

重建脚本不应假定拟合参数文件永远采用固定的列顺序。用户可以在重建脚本中手动指定输入列对应的参数含义。

如果参数文件带有列名，可以按列名映射：

```python
PARAMETER_MAPPING = {
    "x": "x",
    "y": "y",
    "peak_id": "peak_id",
    "center": "position",
    "amplitude": "area",
    "sigma": "width",
}
```

如果参数文件没有列名，可以按列序号映射：

```python
PARAMETER_COLUMNS = {
    "x": 0,
    "y": 1,
    "peak_id": 2,
    "center": 3,
    "amplitude": 4,
    "sigma": 5,
}
```

如果输入参数使用的不是模型所需的形式，也可以在映射处指定转换。例如将半高宽转换为 Gaussian 模型需要的 `sigma`：

```python
PARAMETER_MAPPING = {
    "center": {"column": "position"},
    "sigma": {"column": "fwhm", "conversion": "fwhm_to_sigma"},
}
```

参数列映射解决的是“输入文件中的某一列代表什么”，与线型选择是两个独立问题。

### 线型选择

项目不设计额外的自动线型转换层。用户直接在拟合脚本顶部选择要调用的函数或类。

例如选择 Gaussian：

```python
from raman.fitting import gaussian

FIT_METHOD = gaussian
```

改用 Lorentzian 时，只需要更换导入和调用对象：

```python
from raman.fitting import lorentzian

FIT_METHOD = lorentzian
```

拟合脚本的主体流程保持不变：

```python
result = FIT_METHOD(x, intensity, **FIT_OPTIONS)
```

重建脚本采用同样的方式选择对应重建函数：

```python
from raman.reconstruction import reconstruct_gaussian

RECONSTRUCT_METHOD = reconstruct_gaussian
```

改用 Lorentzian 时：

```python
from raman.reconstruction import reconstruct_lorentzian

RECONSTRUCT_METHOD = reconstruct_lorentzian
```

每种线型的拟合函数和重建函数应保持统一接口。拟合和重建时应选择同一种模型，但不需要通过额外框架自动推断或转换模型。

混合线型作为单独的拟合或重建函数实现。例如该函数可以明确规定不同峰使用不同模型：

```python
PEAK_MODELS = [gaussian, lorentzian, voigt]
```

这样可以通过修改工作脚本顶部的函数或类，直观看到当前使用的线型，并保持每个脚本的处理逻辑简单。
