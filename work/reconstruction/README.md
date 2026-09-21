# 光谱重建与运算

`reconstruct_from_parameters.py` 保留原有重建工作流。新增的 `reconstruct_spectrum.py` 支持新混合拟合参数表；`add_spectra.py` 将两条 CSV 光谱相加；`subtract_spectra.py` 将第一条光谱减去第二条光谱。

```bash
python work/reconstruction/reconstruct_from_parameters.py --x 0 --y 0
python work/reconstruction/reconstruct_spectrum.py
python work/reconstruction/add_spectra.py
python work/reconstruction/subtract_spectra.py
```

在 `reconstruct_spectrum.py` 顶部修改 `RECONSTRUCT_METHOD` 可切换旧参数表的 Gaussian、Lorentzian 或 Voigt 重建；新 `fit_scan.py` 输出的参数表带有 `model` 列，脚本会自动按 `lorentzian` 或 `lopc` 读取对应参数。`SHIFT_SOURCE_PATH` 只用于提供 Raman 位移轴，默认读取 baseline 输出的校正 TIFF，也可以改成单条两列 CSV。修改 `X_COORDINATE`、`Y_COORDINATE` 选择点；修改 `PARAMETER_MAPPING` 指定参数表列的含义。加减脚本顶部的三个路径直接指定输入和输出文件。
