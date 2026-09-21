# 可视化

本目录的每个脚本都可以直接运行。修改脚本顶部的输入路径、空间坐标、参数名和输出路径后执行 `python xxx.py`。

`plot_single_spectrum.py` 读取原始 TIFF 和背景 TIFF，绘制一个空间点的原始、背景和校正光谱。`plot_spectra_comparison.py` 读取顶部 `INPUT_PATHS` 中的多条两列 CSV，第一个画散点，其余画细线。`plot_parameter_heatmap.py` 读取逐点拟合参数表，绘制顶部 `PARAMETER_NAME` 指定参数的空间热力图。`__init__.py` 只是包声明，`output/` 保存图片。
