from __future__ import annotations

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import random


@dataclass(frozen=True)
class PriceSeries:
    # Minimal representation for factor math
    # Assumes daily points in chronological order.
    closes: List[float]


def _deterministic_seed(ticker: str) -> int:
    return abs(hash(ticker)) % (2**31)


def _stub_price_series(tickers: List[str], days: int) -> Dict[str, PriceSeries]:
    """Fallback stub data if real provider is unavailable."""
    out: Dict[str, PriceSeries] = {}
    for t in tickers:
        seed = _deterministic_seed(t)
        rng = random.Random(seed)

        drift = (seed % 17 - 8) / 1000.0  # [-0.008..0.008]
        vol = 0.02 + (seed % 13) / 1000.0

        price = 100.0 + (seed % 97)
        closes: List[float] = []
        for _ in range(days):
            shock = rng.gauss(0, vol)
            price = max(1.0, price * (1.0 + drift + shock))
            closes.append(price)

        out[t] = PriceSeries(closes=closes)

    return out


def fetch_price_series(tickers: List[str], days: int = 120) -> Dict[str, PriceSeries]:
    """Fetch daily historical adjusted closes for tickers.

    Uses yfinance.
    Falls back to deterministic stub data if network/provider fails.
    """

    try:
        import yfinance as yf

        # Download enough calendar days to cover ~trading days.
        # yfinance 'period' is simpler than computing dates.
        # 120 trading days ~= 6 months.
        period = "6mo"
        df = yf.download(
            tickers=tickers,
            period=period,
            interval="1d",
            auto_adjust=True,  # adjusted close proxy
            group_by="ticker",
            threads=False,
            progress=False,
        )

        out: Dict[str, PriceSeries] = {}

        for t in tickers:
            # yfinance returns MultiIndex columns when multiple tickers.
            # Prefer the 'Close' column if present.
            try:
                if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
                    close = df[t]["Close"]
                else:
                    # single ticker case
                    close = df["Close"]

                closes = [float(x) for x in close.dropna().tolist()]
            except Exception:
                closes = []

            # Ensure we have at least `days` points; if not, keep whatever we have.
            out[t] = PriceSeries(closes=closes[-days:] if len(closes) >= days else closes)

        return out
    except Exception:
        return _stub_price_series(tickers, days)


def fetch_benchmark_series(benchmarks: List[str], days: int = 120) -> Dict[str, PriceSeries]:
    """Alias for fetch_price_series for now."""
    return fetch_price_series(benchmarks, days=days)


