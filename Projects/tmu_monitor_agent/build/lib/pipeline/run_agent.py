from __future__ import annotations

from dataclasses import dataclass

from src.ingestion.yahoo_news import fetch_yahoo_news_stub
from src.mapping.ticker_mapper import TMU_SECTOR_MAP, map_ticker_to_sector
from src.nlp.sentiment_llm import extract_sentiment_stub
from src.recommendation.logic import recommend_from_sentiments
from src.reporting.schemas import AgentRunResult


def run_once() -> AgentRunResult:
    """Single daily run: fetch -> sentiment -> recommend -> report."""

    # 1) Ingest (best-effort placeholder)
    raw_items = fetch_yahoo_news_stub()

    # 2) Map + NLP (sentiment/catalyst)
    enriched = []
    for item in raw_items:
        ticker = item.get("ticker")
        if not ticker:
            continue
        sector = map_ticker_to_sector(ticker)
        if not sector:
            continue

        sentiment_json = extract_sentiment_stub(ticker=ticker, text=item.get("summary") or item.get("title") or "")
        enriched.append(
            {
                "ticker": ticker,
                "sector": sector,
                "title": item.get("title"),
                "summary": item.get("summary"),
                **sentiment_json,
            }
        )

    # 3) Recommend
    recs = recommend_from_sentiments(enriched)

    return AgentRunResult(items=enriched, recommendations=recs)

