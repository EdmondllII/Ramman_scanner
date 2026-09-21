"""将两条两列 CSV 光谱相加。"""

from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.io import read_csv_spectrum

FIRST_PATH = Path("first.csv")  # 第一条光谱，输出使用它的 Raman 位移轴
SECOND_PATH = Path("second.csv")  # 第二条光谱
OUTPUT_PATH = Path("work/reconstruction/output/sum.csv")  # 相加结果

x1, y1 = read_csv_spectrum(FIRST_PATH)
x2, y2 = read_csv_spectrum(SECOND_PATH)
y2_on_x1 = y2 if np.array_equal(x1, x2) else np.interp(x1, x2, y2)  # 坐标不同则插值
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
np.savetxt(OUTPUT_PATH, np.column_stack((x1, y1 + y2_on_x1)), delimiter=",", header="raman_shift,intensity", comments="")
print(f"已保存相加光谱：{OUTPUT_PATH}")
