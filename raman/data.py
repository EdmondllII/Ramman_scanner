"""拉曼处理方法共用的数据结构。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class RamanData:
    """表示一维拉曼光谱、二维强度图或光谱立方体。"""

    kind: str
    x: np.ndarray
    intensity: np.ndarray
    y: np.ndarray | None = None
    spectral_axis: np.ndarray | None = None
