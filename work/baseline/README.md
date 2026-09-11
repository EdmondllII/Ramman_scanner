# 基线矫正

修改 `run.py` 顶部的常量，或传入 `--input`、`--output` 和 `--x/--y` 范围参数。
脚本逐个处理 `(y, x)` 光谱，并写入 `output/background.tif` 和 `output/metadata.json`。

TIFF 只包含估计出的背景。校正光谱在后续按 `raw - background` 计算。
