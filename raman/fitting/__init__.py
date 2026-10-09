"""当前可用的光谱处理、峰检测和拟合方法。"""

from .gaussian import fit as gaussian
from .lopc import fit as lopc
from .lopc_fh import fit as lopc_fh
from .lorentzian import fit as lorentzian
from .lopc_fh_convolved import fit as lopc_fh_convolved
from .peak_detection import detect_peaks, spectrum_data
from .voigt import fit as voigt

__all__ = [
    "detect_peaks",
    "gaussian",
    "lopc",
    "lopc_fh",
    "lorentzian",
    "lopc_fh_convolved",
    "spectrum_data",
    "voigt",
]
