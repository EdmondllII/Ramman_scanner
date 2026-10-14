"""从三维校正谱和重建谱中提取指定点并绘制对比图。"""
from pathlib import Path
import sys
import numpy as np
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib.pyplot as plt
from raman.io import read_tiff
CORRECTED_PATH=Path("work/baseline/output/corrected.tif")
RECONSTRUCTED_PATH=Path("work/reconstruction/output/reconstructed_fh.tif")
X_COORDINATE,Y_COORDINATE=0,0
READER_OPTIONS={"raman_shift_start":350.0,"raman_shift_end":800.0}
OUTPUT_PATH=Path("work/visualization/output/comparison_fh.png")
corrected=read_tiff(CORRECTED_PATH,**READER_OPTIONS)
reconstructed=read_tiff(RECONSTRUCTED_PATH,**READER_OPTIONS)
if corrected.spectral_axis is None or reconstructed.spectral_axis is None:
    raise ValueError("输入 TIFF 缺少 Raman 位移轴")
if corrected.intensity.shape != reconstructed.intensity.shape:
    raise ValueError("校正谱与重建谱的立方体形状不一致")
if not np.allclose(corrected.spectral_axis,reconstructed.spectral_axis):
    raise ValueError("校正谱与重建谱的位移轴不一致")
shifts=corrected.spectral_axis
target=corrected.intensity[Y_COORDINATE,X_COORDINATE]
fitted=reconstructed.intensity[Y_COORDINATE,X_COORDINATE]
if not np.isfinite(target).any() or not np.isfinite(fitted).any():
    raise ValueError("指定空间点没有有效的校正谱或重建谱")
figure,axis=plt.subplots(figsize=(8,4.5))
axis.scatter(shifts,target,s=1,color="black",label="corrected")
axis.plot(shifts,fitted,linewidth=0.5,color="red",label="reconstructed_fh")
axis.set(xlabel="Raman shift",ylabel="Intensity")
axis.set_title(f"FH comparison, x={X_COORDINATE}, y={Y_COORDINATE}")
axis.legend()
figure.tight_layout()
OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True)
figure.savefig(OUTPUT_PATH,dpi=150)
plt.close(figure)
print(f"已保存图片：{OUTPUT_PATH}")
