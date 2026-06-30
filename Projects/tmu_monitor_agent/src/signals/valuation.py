from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from src.data.fundamentals import Fundamentals


@dataclass(frozen=True)
class ValuationSignals:
    pe: float
    ev_to_sales: float
    ev_to_ebitda: float
    free_cash_flow_yield: float


def compute_valuation_signals(fundamentals: Dict[str, Fundamentals]) -> Dict[str, ValuationSignals]:
    out: Dict[str, ValuationSignals] = {}
    for t, f in fundamentals.items():
        out[t] = ValuationSignals(
            pe=float(f.pe),
            ev_to_sales=float(f.ev_to_sales),
            ev_to_ebitda=float(f.ev_to_ebitda),
            free_cash_flow_yield=float(f.free_cash_flow_yield),
        )
    return out

