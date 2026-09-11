# 峰拟合

`run.py` 读取原始光谱立方体和基线工作流生成的 `background.tif`，然后对每个选定
空间点分别进行峰检测和拟合。结果写入长表 `output/fit_parameters.csv` 及
说明性元数据 `metadata.json`。
