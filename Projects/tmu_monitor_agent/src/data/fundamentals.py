from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import random


@dataclass(frozen=True)
class Fundamentals:
    gross_margin: float
    operating_margin: float
    free_cash_flow_margin: float

    pe: float
    ev_to_sales: float
    ev_to_ebitda: float
    free_cash_flow_yield: float


def _deterministic_seed(ticker: str) -> int:
    return abs(hash(ticker)) % (2**31)


def fetch_fundamentals(tickers: List[str]) -> Dict[str, Fundamentals]:
    """Fetch fundamentals.

    Initial deterministic stub.
    Replace with real financial statement + metrics extraction later.
    """
    out: Dict[str, Fundamentals] = {}
    for t in tickers:
        seed = _deterministic_seed(t)
        rng = random.Random(seed)

        # quality
        gross_margin = min(0.95, max(0.05, 0.25 + rng.random() * 0.5))
        operating_margin = min(0.8, max(-0.2, 0.05 + rng.random() * 0.4))
        free_cash_flow_margin = min(0.6, max(-0.3, 0.02 + rng.random() * 0.35))

        # valuation (rough ranges)
        pe = max(5.0, 10.0 + rng.random() * 60.0)
        ev_to_sales = max(0.5, 1.0 + rng.random() * 15.0)
        ev_to_ebitda = max(3.0, 6.0 + rng.random() * 35.0)

        # FCF yield (higher better)
        free_cash_flow_yield = min(0.25, max(0.0, 0.02 + rng.random() * 0.12))

        out[t] = Fundamentals(
            gross_margin=gross_margin,
            operating_margin=operating_margin,
            free_cash_flow_margin=free_cash_flow_margin,
            pe=pe,
            ev_to_sales=ev_to_sales,
            ev_to_ebitda=ev_to_ebitda,
            free_cash_flow_yield=free_cash_flow_yield,
        )

    return out

