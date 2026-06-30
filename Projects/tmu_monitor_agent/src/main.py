from __future__ import annotations

import argparse
import os
from dataclasses import asdict
from datetime import datetime
from typing import List

import yaml

from src.data.fundamentals import fetch_fundamentals
from src.data.market_data import fetch_price_series
from src.data.news import fetch_external_news_signals
from src.llm.narrative import generate_narrative
from src.reports.report import build_text_report
from src.scoring.score import score_universe
from src.signals.momentum import compute_momentum_signals
from src.signals.quality import compute_quality_signals
from src.signals.risk import compute_risk_signals
from src.signals.valuation import compute_valuation_signals


def _load_universe(config_path: str) -> List[str]:
    cfg = yaml.safe_load(open(config_path, "r", encoding="utf-8"))
    u = cfg.get("universe", {})
    tickers = []
    for k in ["mega_cap", "semiconductors", "software_saas"]:
        tickers.extend(u.get(k, []))
    # de-dup preserve order
    seen = set()
    out = []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="US investor recommendation model")
    p.add_argument("--config", default="config/universe.yml")
    p.add_argument("--report-dir", default="reports")
    return p


def main() -> None:
    args = build_arg_parser().parse_args()

    config_path = args.config
    report_dir = args.report_dir
    os.makedirs(report_dir, exist_ok=True)

    # universe
    universe = _load_universe(config_path)

    # data
    price_series = fetch_price_series(universe, days=120)
    fundamentals = fetch_fundamentals(universe)
    news_signals = fetch_external_news_signals(universe)

    # signals
    mom = compute_momentum_signals(price_series)
    qual = compute_quality_signals(fundamentals)
    val = compute_valuation_signals(fundamentals)
    risk = compute_risk_signals(price_series, news_signals)

    # scoring
    recs, _meta = score_universe(
        universe=universe,
        momentum=mom,
        quality=qual,
        valuation=val,
        risk=risk,
        config_path=config_path,
    )

    # LLM narrative (optional; deterministic fallback)
    include_narrative = True
    if include_narrative:
        # attach narrative to top N (ticker recommendations are frozen dataclasses)
        # so rebuild objects with updated llm_narrative.
        updated: list = []
        for r in recs:
            if r.ticker in {x.ticker for x in recs[:5]}:
                narrative = generate_narrative(
                    ticker=r.ticker,
                    score=r.score,
                    label=r.label,
                    factors=r.factors,
                )
                updated.append(
                    type(r)(
                        ticker=r.ticker,
                        score=r.score,
                        label=r.label,
                        factors=r.factors,
                        risk_flags=r.risk_flags,
                        llm_narrative=narrative,
                    )
                )
            else:
                updated.append(r)
        recs = updated


    report_title = "US Stock Investor Recommendation Report"
    body = build_text_report(recommendations=recs, report_title=report_title)

    # append narrative for top tickers
    lines = [body]
    lines.append("\nNarratives (top 5)")
    lines.append("------------------")
    for r in recs[:5]:
        lines.append(f"\n{r.ticker} | {r.label} | score={r.score:.3f}")
        n = r.llm_narrative
        if not n:
            continue
        lines.append("Bull case:")
        for x in n.get("bull_case", []):
            lines.append(f"- {x}")
        lines.append("Bear case:")
        for x in n.get("bear_case", []):
            lines.append(f"- {x}")
        lines.append("Key risks:")
        for x in n.get("key_risks", []):
            lines.append(f"- {x}")
        lines.append("Further to be checked:")
        for x in n.get("further_to_be_checked", []):
            lines.append(f"- {x}")
        lines.append("Watchlist:")
        for x in n.get("watchlist", []):
            lines.append(f"- {x}")

    ts = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(report_dir, f"us_investor_recommendations_{ts}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"US model report written: {out_path}")


if __name__ == "__main__":
    main()

