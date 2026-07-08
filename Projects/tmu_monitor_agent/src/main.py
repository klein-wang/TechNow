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
from src.ingestion.cnbc_technology_news import fetch_cnbc_technology_news

from src.llm.narrative import generate_narrative
from src.reports.report import build_text_report
from src.scoring.score import score_universe
from src.signals.momentum import compute_momentum_signals
from src.signals.quality import compute_quality_signals
from src.signals.risk import compute_risk_signals
from src.signals.valuation import compute_valuation_signals

import json


def safe_last_n(seq, n: int):
    if seq is None:
        return []
    if len(seq) <= n:
        return list(seq)
    return list(seq[-n:])


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

    # Raw news (CNBC scraping) + derived news signals (stub)
    cnbc_news_items = fetch_cnbc_technology_news()
    news_signals = fetch_external_news_signals(universe)


    # audit/run folder
    run_date = datetime.now().strftime("%Y-%m-%d")
    run_dir = os.path.join(report_dir, "us_model_runs", run_date)
    os.makedirs(run_dir, exist_ok=True)


    # signals
    mom = compute_momentum_signals(price_series)
    qual = compute_quality_signals(fundamentals)
    val = compute_valuation_signals(fundamentals)
    risk = compute_risk_signals(price_series, news_signals)

    # scoring
    recs, meta = score_universe(


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

    # Audit artifacts (inputs + intermediate signals + last-10 closes)
    audit = {
        "run_date": run_date,
        "config_path": config_path,
        "universe": universe,
        "inputs": {
            "price_series_last_10_closes": {t: safe_last_n(ps.closes, 10) for t, ps in price_series.items()},
            "cnbc_news_items": cnbc_news_items,
        },
        "signals": {
            "momentum": {t: asdict(mom[t]) for t in mom},
            "quality": {t: asdict(qual[t]) for t in qual},
            "valuation": {t: asdict(val[t]) for t in val},
            "risk": {t: asdict(risk[t]) for t in risk},
            "news_signals": {t: asdict(news_signals[t]) for t in news_signals},
        },
        "recommendations": [
            {
                "ticker": r.ticker,
                "score": r.score,
                "label": r.label,
                "factors": r.factors,
                "risk_flags": r.risk_flags,
                "llm_narrative": r.llm_narrative,
            }
            for r in recs
        ],
        "generated_at": datetime.now().isoformat(),
    }

    # Supplementary news report (plain text, for quick audit)
    news_lines: list[str] = []
    news_lines.append("CNBC Ingested News Items")
    news_lines.append("==========================")
    news_lines.append("")
    news_lines.append(f"Items ingested: {len(cnbc_news_items)}")
    news_lines.append("")

    for item in cnbc_news_items:
        ticker = item.get("ticker", "")
        title = (item.get("title") or "").strip()
        summary = (item.get("summary") or "").strip()
        url = (item.get("url") or "").strip()
        news_lines.append(f"{ticker} | {title} | {summary}")
        if url:
            news_lines.append(f"  url: {url}")

    news_lines.append("")
    news_lines.append("Derived News Signals (stub)")
    news_lines.append("=============================")
    news_lines.append("")
    for t in universe:
        if t not in news_signals:
            continue
        ns = news_signals[t]
        news_lines.append(
            f"{t} | regulatory_topic_present={ns.regulatory_topic_present} | "
            f"regulatory_risk_score={ns.regulatory_risk_score:.3f}"
        )

    news_path = os.path.join(run_dir, "news.txt")
    with open(news_path, "w", encoding="utf-8") as f:
        f.write("\n".join(news_lines))


    report_audit_path = os.path.join(run_dir, "report.txt")
    with open(report_audit_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    audit_path = os.path.join(run_dir, "run.json")
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2, default=str)

    print(f"US model report written: {out_path}")
    print(f"US model audit written: {audit_path}")



if __name__ == "__main__":
    main()

