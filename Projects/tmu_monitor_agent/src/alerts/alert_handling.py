from __future__ import annotations

from typing import List

from src.scoring.score import TickerRecommendation


def build_alerts(recommendations: List[TickerRecommendation]) -> List[str]:
    """Create human-readable alert lines based on labels/flags."""
    alerts: List[str] = []
    for r in recommendations:
        if r.label in {"high risk", "avoid/wait"} or any(r.risk_flags):
            alerts.append(f"ALERT {r.ticker}: label={r.label} score={r.score:.3f} flags={r.risk_flags}")
    return alerts

