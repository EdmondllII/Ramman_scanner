# 拉曼扫描数据分析

这是一个拉曼扫描数据处理程序。安装依赖后，直接在项目目录运行：
```text
conda activate raman

python -m pip install -r requirements.txt
python main.py
```

## 文件说明

- `main.py`：唯一入口。在顶部直接指定读取器、基线矫正方法和拟合方法。
- `raman/io/`：TXT 与 TIFF 数据读取实现；可用读取器在 `raman/io/__init__.py` 中列出。
- `raman/baseline/`：AsLS 与 airPLS 基线矫正实现；可用方法在 `raman/baseline/__init__.py` 中列出。
- `raman/fitting/`：单条光谱的峰检测和 Gaussian 拟合实现；可用方法在 `raman/fitting/__init__.py` 中列出。
- `raman/output.py`：将光谱、基线、拟合曲线及拟合参数写入 `raman_output/`。

修改 `main.py` 顶部的 `READ_DATA`、`BASELINE_METHOD`、`FIT_METHOD` 及各自的参数字典，即可选择本次流程使用的方法。TIFF 光谱立方体会对每个空间点的光谱分别处理，并将逐点结果保存到 `cube_processed.npz` 和 `cube_fit_parameters.csv`。
