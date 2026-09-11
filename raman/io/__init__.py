"""当前可用的数据读取方法。"""

from .tiff_reader import read_tiff
from .spectrum_reader import read_csv_spectrum
from .txt_reader import read_txt

__all__ = ["read_csv_spectrum", "read_tiff", "read_txt"]
