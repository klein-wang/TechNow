from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from src.data.market_data import PriceSeries


@dataclass(frozen=True)
class MomentumSignals:
    ret_20d: float
    ret_60d: float
    price_to_ma_50d: float
    price_to_ma_100d: float


def _pct_return(closes: List[float], window: int) -> float:
    if len(closes) <= window:
        return 0.0
    start = closes[-window]
    end = closes[-1]
    if start == 0:
        return 0.0
    return (end / start) - 1.0


def _moving_average_ratio(closes: List[float], window: int) -> float:
    if len(closes) < window:
        return 1.0
    ma = float(np.mean(closes[-window:]))
    if ma == 0:
        return 1.0
    return float(closes[-1] / ma)


def compute_momentum_signals(price_series: Dict[str, PriceSeries]) -> Dict[str, MomentumSignals]:
    out: Dict[str, MomentumSignals] = {}
    for ticker, ps in price_series.items():
        closes = ps.closes
        out[ticker] = MomentumSignals(
            ret_20d=_pct_return(closes, 20),
            ret_60d=_pct_return(closes, 60),
            price_to_ma_50d=_moving_average_ratio(closes, 50),
            price_to_ma_100d=_moving_average_ratio(closes, 100),
        )
    return out

