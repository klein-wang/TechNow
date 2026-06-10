from __future__ import annotations

from typing import Any


def fetch_yahoo_news_stub() -> list[dict[str, Any]]:
    """Best-effort Yahoo ingestion placeholder.

    Yahoo News endpoints vary and may require query parameters / scraping.
    To keep this prototype runnable without API keys, we return a small deterministic set.

    Replace this with real Yahoo News integration when ready.
    """

    # Example TMU tickers to bootstrap the pipeline.
    return [
        {
            "ticker": "AAPL",
            "title": "AI regulation headlines spark tech sector debate",
            "summary": "New policy proposals around AI transparency could impact product roadmaps and compliance costs.",
        },
        {
            "ticker": "NFLX",
            "title": "Streaming subscriber growth supports media optimism",
            "summary": "Analysts cite steady subscriber additions and margin resilience despite competition.",
        },
        {
            "ticker": "DUK",
            "title": "Grid infrastructure investment accelerates utility upgrades",
            "summary": "Utilities announce capex plans to modernize grids and improve reliability ahead of demand growth.",
        },
    ]

