from __future__ import annotations

from typing import Literal


def extract_sentiment_stub(*, ticker: str, text: str) -> dict:
    """Deterministic sentiment extraction stub.

    Output format follows the design doc JSON fields.

    Replace with real LLM integration (and DK-CoT prompting) later.
    """

    t = ticker.upper()
    if t in {"AAPL", "MSFT", "NVDA"}:
        score = 0.62
        catalyst = "AI transparency/regulation proposals"
        impact = "Regulatory may increase compliance costs but also clarifies adoption"
    elif t in {"NFLX", "DIS", "CMCSA"}:
        score = 0.78
        catalyst = "Subscriber growth and margin resilience"
        impact = "Positive demand signals for streaming ecosystem"
    else:
        # Utilities
        score = -0.12
        catalyst = "Capex/grid modernization announcements"
        impact = "Neutral-to-slightly positive reliability upgrades"

    # confidence heuristic: choose low if score near 0
    confidence: Literal["high", "low"] = "low" if abs(score) < 0.2 else "high"

    return {
        "sentiment_score": float(score),
        "key_catalyst": catalyst,
        "sector_impact": impact,
        "confidence": confidence,
    }

