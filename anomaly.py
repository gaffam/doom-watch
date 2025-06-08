"""Anomaly detection utilities using Prophet."""

from typing import Dict, List

import logging
import numpy as np
import pandas as pd
from prophet import Prophet


def detect_anomaly(data_window: List[Dict[str, float]]) -> bool:
    """Return True if the latest aggregated value deviates above forecast."""
    if len(data_window) < 3:
        return False

    # Average values into a single series
    df = pd.DataFrame(data_window)
    df["y"] = df.mean(axis=1)
    df["ds"] = pd.date_range(end=pd.Timestamp.today(), periods=len(df))

    try:
        model = Prophet()
        model.fit(df[["ds", "y"]])
        future = model.make_future_dataframe(periods=1)
        forecast = model.predict(future)
        return forecast["yhat"].iloc[-1] > forecast["yhat_upper"].iloc[-1]
    except Exception as exc:
        logging.warning("prophet anomaly detection failed: %s", exc)
        return False
