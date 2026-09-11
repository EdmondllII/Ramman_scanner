"""从一个两列 CSV 光谱中减去另一个光谱。"""

try:
    from .add_spectra import combine
except ImportError:  # 直接运行此文件时使用备用导入方式。
    from add_spectra import combine


def main() -> None:
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path); parser.add_argument("second", type=Path); parser.add_argument("output", type=Path)
    args = parser.parse_args(); combine(args.first, args.second, args.output, sign=-1.0)


if __name__ == "__main__":
    main()
