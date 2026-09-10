"""当前可用的基线矫正方法。"""

from .airpls import correct as airpls
from .asls import correct as asls

__all__ = ["airpls", "asls"]
