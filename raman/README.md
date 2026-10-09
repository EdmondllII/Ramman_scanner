# raman

- `__init__.py`：定义 `raman` 包并导出公共数据类型。
- `data.py`：定义 `RamanData`，统一表示光谱、二维扫描图和 TIFF 光谱立方体。
- `lineshapes.py`：公共 LOPC、完整 A 项及 Gaussian 仪器卷积线型公式，不执行优化；拟合和重建共同调用。
- `io/`：提供 TXT 和 TIFF 数据读取方法。
- `baseline/`：提供基线矫正方法。
- `fitting/`：提供峰检测和线形拟合方法。
- `reconstruction/`：提供与拟合参数一致的 Gaussian、Lorentzian、LOPC 单谱重建方法。
- `evaluation.py`：只根据两条已对齐的一维光谱计算误差指标，不读取文件、不重建、不拟合。

扫描区域遍历、结果文件和绘图由项目根目录的 `work/` 包负责；`raman/` 的算法模块只接收内存中的数据和参数，不读取工作流文件、不创建输出目录、不处理空间循环。

`io/` 是唯一负责文件读取的子包；`lineshapes.py`、`baseline/`、`fitting/`、`reconstruction/` 和 `evaluation.py` 都是纯算法接口。输出文件、参数表、评估报告和图片由 `work/` 脚本保存。

两个 Adam 模块按项目的明确配置，从本机指定 Conda 环境加载 Torch；这项环境适配保留，不读写实验数据或结果文件。
