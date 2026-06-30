from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import random



@dataclass(frozen=True)
class PriceSeries:
    # Minimal representation for factor math
    # Assumes equally spaced daily points.
    closes: List[float]


def _deterministic_seed(ticker: str) -> int:
    return abs(hash(ticker)) % (2**31)


def fetch_price_series(tickers: List[str], days: int = 120) -> Dict[str, PriceSeries]:
    """Fetch price series for tickers.

    Initial implementation is deterministic stub data so the end-to-end
    recommendation pipeline runs.

    Replace this with a real provider (yfinance/Polygon/etc.) later.
    """

    out: Dict[str, PriceSeries] = {}
    for t in tickers:
        seed = _deterministic_seed(t)
        rng = random.Random(seed)

        # create a pseudo-random walk with a small drift depending on ticker
        drift = (seed % 17 - 8) / 1000.0  # [-0.008..0.008]
        vol = 0.02 + (seed % 13) / 1000.0

        price = 100.0 + (seed % 97)
        closes: List[float] = []
        for i in range(days):
            shock = rng.gauss(0, vol)
            price = max(1.0, price * (1.0 + drift + shock))
            closes.append(price)

        out[t] = PriceSeries(closes=closes)

    return out


def fetch_benchmark_series(benchmarks: List[str], days: int = 120) -> Dict[str, PriceSeries]:
    """Alias for fetch_price_series for now."""
    return fetch_price_series(benchmarks, days=days)

