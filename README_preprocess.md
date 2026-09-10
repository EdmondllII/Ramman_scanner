# 拉曼扫描数据读取、预处理与峰特征提取

本目录目前包含两个可以直接运行的 Python 脚本。脚本顶部使用固定配置，
不需要命令行参数。

## 项目文件说明

- `raman/io/`：读取 TXT 或 TIFF 数据；
- `raman/baseline/`：使用 pybaselines 执行基线矫正；
- `raman/fitting/`：检测峰并使用 lmfit 执行线形拟合；
- `main.py`：选择并串联上述方法。
- `requirements.txt`：运行上述程序所需的 Python 依赖，包括 `tifffile`；
- `README_preprocess.md`：本文档，说明运行方法、配置项和输出结果。

## 依赖安装

在项目目录中运行：

```text
python -m pip install -r requirements.txt
```

依赖包括：

- `numpy`：数组和数值计算；
- `scipy`：Savitzky-Golay 平滑、峰检测和半高宽计算；
- `matplotlib`：生成预览图和特征图。

## 第一步：读取和预处理

运行：

```text
python main.py
```

修改 `main.py` 顶部的 `INPUT_PATH` 可以分析其他文件，
`OUTPUT_DIR` 用于指定输出目录。

脚本可以识别三种输入：

1. 两列数据：第一列为位置（例如拉曼位移），第二列为强度；
2. 二维扫描矩阵：第一行为横坐标，第一列为纵坐标，其余部分为强度矩阵；
3. 三维 TIFF 光谱立方体：两个空间维度和一个 Raman 光谱维度。

当前示例文件属于第二种格式，首行省略了左上角的空单元，脚本会自动补齐。

默认预处理是保守的：只填补非有限值，不自动删除极端值，也不平滑。这样可以
避免在尚未确认峰形之前改变真实信号。若确认需要平滑，可将顶部的
`SMOOTH_WINDOW` 改为大于 `SMOOTH_POLYORDER` 的奇数，例如 `7`。

### 预处理输出文件

输出目录默认为 `raman_preprocessed/`：

- `scan_raw.csv`：二维扫描的原始数据，第一行和第一列保留坐标；
- `scan_processed.csv`：二维扫描的预处理数据；
- `spectrum_processed.csv`：两列光谱的原始强度和预处理强度；
- `preview.png`：原始数据和预处理数据的对比图；
- `README.txt`：本次处理的简要说明。

预处理阶段目前不进行基线扣除，也不提取峰。

## 第二步：简单峰提取

运行：

```text
python main.py
```

对于二维扫描，脚本默认沿 `y` 方向对所有行求平均，得到一条沿 `x` 方向的
代表性曲线，然后检测孤立的局部最大峰。对于两列光谱，则直接使用该光谱。

**重要：当前示例文件是二维强度矩阵，不是光谱立方体。** 它只有一个二维
强度值 `intensity(y, x)`，没有“每个空间点对应的一条 Raman 位移-强度光谱”。
所以当前流程得到的是平均曲线上的局部最大值，不能解释为
真正的 Raman 峰，也不能据此生成物理意义正确的“每个峰位置/FWHM 空间热力图”。
要生成这类热力图，需要输入 `intensity(y, x, raman_shift)` 三维数据，或一组
带有空间坐标的两列光谱文件。拿到这种数据后，可以对每个空间点独立提峰，再把
同一个峰的 `position`、`fwhm`、`height` 等值还原成二维热力图。

可以修改脚本顶部的配置：

- `PROFILE_AXIS = "x"`：二维扫描沿横坐标方向提峰；
- `PROFILE_AXIS = "y"`：二维扫描沿纵坐标方向提峰；
- `SMOOTH_WINDOW`：峰检测前的平滑窗口，`0` 表示不平滑；
- `MIN_PROMINENCE`：峰显著性阈值，`None` 表示根据数据噪声自动估计；
- `MIN_DISTANCE_POINTS`：相邻峰至少间隔的采样点数。

### 峰特征定义

`peaks.csv` 中每一行对应一个峰：

- `peak_id`：按位置从小到大排列的峰编号；
- `position`：峰位置，峰顶使用三点抛物线做了简单亚采样修正；
- `height`：峰顶强度；
- `fwhm`：半高宽，即左右半高位置之差；
- `prominence`：相对于周围基线的峰显著性；
- `left_half_height`：左侧半高位置；
- `right_half_height`：右侧半高位置。

这里的半高宽使用 SciPy 的局部峰宽算法计算，适用于当前明显且近似孤立的峰。
暂未进行复杂基线拟合、Voigt 拟合或重叠峰联合拟合。

### 峰提取输出文件

输出目录默认为 `raman_peaks/`：

- `profile.csv`：用于检测的代表性一维曲线，包含位置和强度；
- `peaks.csv`：所有检测到的峰及其特征；
- `peaks_preview.png`：代表性曲线、峰编号、峰位置和半高宽区间；
- 对旧二维 TXT 输入，`features/*.png` 是代表性曲线上的特征折线图，仅用于检查峰编号和参数。
- 对三维 TIFF 输入，逐峰逐特征的空间热力图写入下方 TIFF 专用的 `heatmaps/` 目录。

## TIFF 光谱立方体

将 `INPUT_PATH` 指向 TIFF 后，程序会使用 `tifffile` 读取三维数据，并自动把最长
的维度视为 Raman 光谱维度，规范为 `(y, x, Raman shift)`。如果 TIFF 没有写入
Raman 位移轴，则按 `RAMAN_SHIFT_START=350` 和 `RAMAN_SHIFT_END=800` 在该维度上
等间隔生成坐标。使用前请确认 TIFF 的最长维度确实是光谱维度。

对于三维 TIFF，流程先对所有空间点求平均，确定峰编号；然后在每个
`(x,y)` 点的光谱中测量同编号峰，并输出真正的空间特征热力图到
`raman_peaks/heatmaps/`：

```text
peak_01_position.png
peak_01_fwhm.png
peak_01_height.png
...
```

每张图对应一个峰和一个特征，横纵坐标是扫描空间的 `x`、`y`，颜色表示该点的
特征值；`feature_maps.npz` 保存所有特征矩阵。旧的二维 TXT 仍只能生成平均剖面
上的局部峰，不能生成这种空间热力图。
