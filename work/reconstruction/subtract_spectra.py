"""从第一条两列 CSV 光谱中减去第二条光谱。"""

from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from raman.io import read_csv_spectrum

FIRST_PATH = Path("first.csv")  # 被减的光谱，输出使用它的 Raman 位移轴
SECOND_PATH = Path("background.csv")  # 要扣除的光谱
OUTPUT_PATH = Path("work/reconstruction/output/difference.csv")  # 相减结果

x1, y1 = read_csv_spectrum(FIRST_PATH)
x2, y2 = read_csv_spectrum(SECOND_PATH)
if not np.array_equal(x1, x2):
    raise ValueError("两条光谱必须使用相同的 Raman 位移轴；请先显式对齐")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
np.savetxt(OUTPUT_PATH, np.column_stack((x1, y1 - y2)), delimiter=",", header="raman_shift,intensity", comments="")
print(f"已保存相减光谱：{OUTPUT_PATH}")
