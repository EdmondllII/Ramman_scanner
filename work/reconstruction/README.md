# 光谱重建

`reconstruct_from_parameters.py` 根据拟合参数表和用户指定的原始光谱坐标重建一个空间点；可以重复使用
`--peak-id` 选择分峰。`add_spectra.py` 和 `subtract_spectra.py` 对两列 CSV
光谱进行加减，不会重新执行拟合。
