from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import random


@dataclass(frozen=True)
class NewsSignal:
    # Minimal representation for regulatory-risk placeholder
    regulatory_topic_present: bool
    regulatory_risk_score: float  # [0,1]


def _deterministic_seed(ticker: str) -> int:
    return abs(hash(ticker)) % (2**31)


def fetch_external_news_signals(tickers: List[str]) -> Dict[str, NewsSignal]:
    """Fetch external market news / macros and extract lightweight flags.

    Stub implementation.

    Later: connect to CNBC / other sources, extract regulatory topics,
    and compute a regulatory-risk score.
    """
    out: Dict[str, NewsSignal] = {}
    for t in tickers:
        seed = _deterministic_seed(t)
        rng = random.Random(seed)

        # pseudo probability of regulatory topic
        p = 0.1 + (seed % 30) / 300.0  # ~0.1..0.2
        regulatory_topic_present = rng.random() < p

        risk = 0.25 + rng.random() * 0.6 if regulatory_topic_present else rng.random() * 0.25
        risk = max(0.0, min(1.0, risk))

        out[t] = NewsSignal(
            regulatory_topic_present=regulatory_topic_present,
            regulatory_risk_score=risk,
        )

    return out

