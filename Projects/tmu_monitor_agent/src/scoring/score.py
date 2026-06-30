from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import yaml

from src.signals.quality import QualitySignals
from src.signals.momentum import MomentumSignals
from src.signals.risk import RiskSignals
from src.signals.valuation import ValuationSignals


@dataclass(frozen=True)
class TickerRecommendation:
    ticker: str
    score: float  # [0,1]
    label: str
    factors: Dict[str, float]
    risk_flags: List[str]
    llm_narrative: Dict[str, Any] | None = None


def _clip01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


def _rank_percentile(values: Dict[str, float], higher_is_better: bool = True) -> Dict[str, float]:
    tickers = list(values.keys())
    arr = np.array([values[t] for t in tickers], dtype=float)

    if not higher_is_better:
        arr = -arr

    ranks = arr.argsort().argsort()  # 0..n-1
    denom = max(1, len(arr) - 1)
    pct = ranks / denom

    return {tickers[i]: float(pct[i]) for i in range(len(tickers))}


def _label_from_score(score: float, labels_cfg: Dict[str, Any]) -> str:
    # labels_cfg keys: strong/medium/low/neutral/avoid_wait
    # keep deterministic ordering
    if score >= labels_cfg["strong"]["min"]:
        return "strong"
    if score >= labels_cfg["medium"]["min"]:
        return "medium"
    if score >= labels_cfg["low"]["min"]:
        return "low"
    if score >= labels_cfg["neutral"]["min"]:
        return "neutral"
    return "avoid/wait"


def score_universe(
    *,
    universe: List[str],
    momentum: Dict[str, MomentumSignals],
    quality: Dict[str, QualitySignals],
    valuation: Dict[str, ValuationSignals],
    risk: Dict[str, RiskSignals],
    config_path: str,
) -> Tuple[List[TickerRecommendation], Dict[str, Any]]:
    cfg = yaml.safe_load(open(config_path, "r", encoding="utf-8"))
    scoring_cfg = cfg.get("scoring", {})
    weights = scoring_cfg.get("weights", {"momentum": 0.25, "quality": 0.25, "valuation": 0.25, "risk": 0.25})
    labels_cfg = scoring_cfg.get("labels", {})

    # Build raw factor aggregates
    mom_raw: Dict[str, float] = {}
    qual_raw: Dict[str, float] = {}
    val_raw: Dict[str, float] = {}
    risk_raw: Dict[str, float] = {}

    for t in universe:
        m = momentum[t]
        q = quality[t]
        v = valuation[t]
        r = risk[t]

        mom_raw[t] = float(0.25 * m.ret_20d + 0.35 * m.ret_60d + 0.20 * (m.price_to_ma_50d - 1.0) + 0.20 * (m.price_to_ma_100d - 1.0))
        qual_raw[t] = float(0.34 * q.gross_margin + 0.33 * q.operating_margin + 0.33 * q.free_cash_flow_margin)

        # valuation: lower multiples better, higher fcf yield better
        val_raw[t] = float(
            0.25 * (-v.pe)
            + 0.25 * (-v.ev_to_sales)
            + 0.25 * (-v.ev_to_ebitda)
            + 0.25 * (v.free_cash_flow_yield * 100)
        )

        # risk: higher volatility/regulatory worse
        risk_raw[t] = float(0.6 * r.volatility_60d_ann + 0.4 * (r.regulatory_risk_score * 100))

    # Normalize to [0,1] percentiles
    mom_pct = _rank_percentile(mom_raw, higher_is_better=True)
    qual_pct = _rank_percentile(qual_raw, higher_is_better=True)
    val_pct = _rank_percentile(val_raw, higher_is_better=True)
    risk_pct = _rank_percentile(risk_raw, higher_is_better=False)  # lower risk_raw -> higher score

    recs: List[TickerRecommendation] = []
    meta: Dict[str, Any] = {"weights": weights}

    for t in universe:
        factor_m = mom_pct.get(t, 0.5)
        factor_q = qual_pct.get(t, 0.5)
        factor_v = val_pct.get(t, 0.5)
        factor_r = risk_pct.get(t, 0.5)

        score = (
            weights.get("momentum", 0.25) * factor_m
            + weights.get("quality", 0.25) * factor_q
            + weights.get("valuation", 0.25) * factor_v
            + weights.get("risk", 0.25) * factor_r
        )
        score = _clip01(float(score))

        label = _label_from_score(score, labels_cfg)

        # high risk overlay
        high_risk_threshold = labels_cfg.get("high_risk", {}).get("risk_min")
        risk_flags: List[str] = []
        if high_risk_threshold is not None:
            # if volatility/regulatory are high => risk_raw high => risk_pct low
            # We'll interpret: risk_pct < (1 - threshold)
            if factor_r < (1.0 - float(high_risk_threshold)):
                label = "high risk"
                risk_flags.append("high_risk_overlay")

        factors = {
            "momentum": float(factor_m),
            "quality": float(factor_q),
            "valuation": float(factor_v),
            "risk": float(factor_r),
        }

        recs.append(TickerRecommendation(ticker=t, score=score, label=label, factors=factors, risk_flags=risk_flags))

    recs_sorted = sorted(recs, key=lambda r: r.score, reverse=True)
    return recs_sorted, meta

