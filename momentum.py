# Momentum feature calculations for economic data.
from typing import Dict, List

import numpy as np


def calc_momentum_features(data_window: List[Dict[str, float]]) -> Dict[str, float]:
    """Return simple trend and volatility acceleration features."""
    if len(data_window) < 2:
        return {"trend": 0.0, "vol_acceleration": 0.0}

    keys = sorted(data_window[0].keys())
    arr = np.array([[d.get(k, 0.0) for k in keys] for d in data_window], dtype=float)

    trend = float(np.mean(arr[-1] - arr[0]))

    mid = len(arr) // 2
    first_std = float(np.std(arr[:mid], ddof=1)) if mid > 1 else 0.0
    last_std = float(np.std(arr[mid:], ddof=1))
    vol_acc = last_std - first_std

    return {"trend": trend, "vol_acceleration": vol_acc}
