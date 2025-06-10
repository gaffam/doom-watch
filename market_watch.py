"""Market monitoring utilities for BIST and search trends."""

from typing import List

import logging
import pandas as pd
import yfinance as yf
from pytrends.request import TrendReq

from alerts import send_telegram


def check_bist_crash(threshold: float = -0.05) -> bool:
    """Return True and alert if BIST-100 drops beyond threshold."""
    try:
        bist = yf.Ticker("XU100.IS")
        df = bist.history(period="2d")
        pct = df["Close"].pct_change().iloc[-1]
        if pct < threshold:
            send_telegram("\U0001F6A8 BIST DROPPING 5%!")
            return True
    except Exception as exc:
        logging.warning("bist check failed: %s", exc)
    return False


def check_google_trends(keywords: List[str]) -> bool:
    """Check if search interest spikes above 80% of 12-month max."""
    try:
        pytrends = TrendReq(hl="tr")
        pytrends.build_payload(keywords, timeframe="today 12-m")
        data = pytrends.interest_over_time()
        if data.empty:
            return False
        scores = data[keywords].iloc[-1]
        if (scores / data[keywords].max()).max() > 0.8:
            return True
    except Exception as exc:
        logging.warning("google trends failed: %s", exc)
    return False

