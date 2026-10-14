"""比较指定点的校正谱与完整 A 项三维重建谱。"""
from pathlib import Path
import sys
import numpy as np
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from raman.io import read_tiff
from work.evaluation.evaluate_fit import evaluate_arrays
TARGET_PATH=Path("work/baseline/output/corrected.tif")
FITTED_PATH=Path("work/reconstruction/output/reconstructed_fh.tif")
X_COORDINATE,Y_COORDINATE=0,0
READER_OPTIONS={"raman_shift_start":350.0,"raman_shift_end":800.0}
OUTPUT_DIR=Path("work/evaluation/output/lopc_fh")
REGIONS={"735_region":(720.0,750.0)}
def main():
    target=read_tiff(TARGET_PATH,**READER_OPTIONS)
    fitted=read_tiff(FITTED_PATH,**READER_OPTIONS)
    if target.spectral_axis is None or fitted.spectral_axis is None:
        raise ValueError("输入 TIFF 缺少 Raman 位移轴")
    if target.intensity.shape != fitted.intensity.shape:
        raise ValueError("校正谱与重建谱的立方体形状不一致")
    if not np.allclose(target.spectral_axis,fitted.spectral_axis):
        raise ValueError("校正谱与重建谱的位移轴不一致")
    target_y=target.intensity[Y_COORDINATE,X_COORDINATE]
    fitted_y=fitted.intensity[Y_COORDINATE,X_COORDINATE]
    if not np.isfinite(target_y).any() or not np.isfinite(fitted_y).any():
        raise ValueError("指定空间点没有有效的校正谱或重建谱")
    evaluate_arrays(target.spectral_axis,target_y,fitted_y,OUTPUT_DIR,
                    f"x{X_COORDINATE}_y{Y_COORDINATE}",regions=REGIONS,
                    input_labels={"target":str(TARGET_PATH),"fitted":str(FITTED_PATH),
                                  "x":X_COORDINATE,"y":Y_COORDINATE})
if __name__=="__main__":
    main()
