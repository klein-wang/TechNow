from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from src.data.fundamentals import Fundamentals


@dataclass(frozen=True)
class QualitySignals:
    gross_margin: float
    operating_margin: float
    free_cash_flow_margin: float


def compute_quality_signals(fundamentals: Dict[str, Fundamentals]) -> Dict[str, QualitySignals]:
    out: Dict[str, QualitySignals] = {}
    for t, f in fundamentals.items():
        out[t] = QualitySignals(
            gross_margin=float(f.gross_margin),
            operating_margin=float(f.operating_margin),
            free_cash_flow_margin=float(f.free_cash_flow_margin),
        )
    return out

