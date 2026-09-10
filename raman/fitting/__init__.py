"""当前可用的光谱处理、峰检测和拟合方法。"""

from .gaussian import fit as gaussian
from .peak_detection import detect_peaks, spectrum_data

__all__ = ["detect_peaks", "gaussian", "spectrum_data"]
