"""比较校正谱与完整 A 项已重建光谱；不读取 C 或执行模型计算。"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from work.evaluation.evaluate_fit import evaluate_files

TARGET_PATH = Path("work/baseline/output/corrected_x0_y0.csv")  # 拟合的目标谱
FITTED_PATH = Path("work/reconstruction/output/reconstructed_fh.csv")  # 先运行 reconstruction
OUTPUT_DIR = Path("work/evaluation/output/lopc_fh")
OUTPUT_STEM = "x0_y0"  # 文件名标签；两条输入须对应同一空间点
REGIONS = {"735_region": (720.0, 750.0)}  # 仅按位移切片；{} 只评估全谱


def main():
    evaluate_files(TARGET_PATH, FITTED_PATH, OUTPUT_DIR, OUTPUT_STEM, regions=REGIONS)


if __name__ == "__main__":
    main()
