from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from src.data.market_data import PriceSeries
from src.data.news import NewsSignal


@dataclass(frozen=True)
class RiskSignals:
    volatility_60d_ann: float
    regulatory_risk_score: float


def _ann_volatility(closes: List[float], window: int = 60) -> float:
    if len(closes) <= window:
        return 0.0
    window_closes = closes[-window:]
    rets = np.diff(window_closes) / np.array(window_closes[:-1])
    if len(rets) == 0:
        return 0.0
    vol = float(np.std(rets)) * float(np.sqrt(252))
    return max(0.0, vol)


def compute_risk_signals(price_series: Dict[str, PriceSeries], news_signals: Dict[str, NewsSignal]) -> Dict[str, RiskSignals]:
    out: Dict[str, RiskSignals] = {}
    for t, ps in price_series.items():
        ns = news_signals.get(t)
        regulatory = float(ns.regulatory_risk_score) if ns else 0.3
        out[t] = RiskSignals(
            volatility_60d_ann=_ann_volatility(ps.closes, 60),
            regulatory_risk_score=regulatory,
        )
    return out

