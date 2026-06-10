from __future__ import annotations

from typing import Any

import requests


YAHOO_RSS_SEARCH_URL = "https://news.google.com/rss/search"


def fetch_yahoo_news_stub() -> list[dict[str, Any]]:
    """Fallback placeholder (deterministic)."""

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


def _parse_rss_items(xml_text: str) -> list[dict[str, Any]]:
    """Very small RSS parser.

    We avoid extra dependencies (like feedparser). This is best-effort.
    """

    import re

    items: list[dict[str, Any]] = []

    for m in re.finditer(r"<item>(.*?)</item>", xml_text, flags=re.DOTALL | re.IGNORECASE):
        block = m.group(1)

        def first(pattern: str) -> str | None:
            mm = re.search(pattern, block, flags=re.DOTALL | re.IGNORECASE)
            if not mm:
                return None
            # mm.group(1) may be None for optional capture groups; normalize to ""
            g = mm.group(1)
            return (g or "").strip()

        title = first(r"<title><!\[CDATA\[(.*?)\]\]>|<title>(.*?)</title>")
        link = first(r"<link>(.*?)</link>")
        desc = first(r"<description>(.*?)</description>")

        # Normalize title
        if "\n" in title:
            title = title.split("\n")[0]

        items.append(
            {
                "title": title or "",
                "link": link or "",
                "summary": desc or "",
            }
        )

    return items


def fetch_yahoo_news(query: str = "Technology Media Utility sector news") -> list[dict[str, Any]]:
    """Fetch Yahoo/Google News RSS search results.

    Output schema expected by the pipeline:
      [{"ticker": str, "title": str, "summary": str}]

    Note: RSS items typically don't include tickers; we use a simple
    title/summary ticker keyword match.

    On failure, returns a diagnostic item (and does not silently fall back),
    so trial runs are debuggable.
    """

    ticker_universe = ["AAPL", "MSFT", "NVDA", "NFLX", "DIS", "CMCSA", "DUK", "NEE", "SO"]

    try:
        params = {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}
        r = requests.get(YAHOO_RSS_SEARCH_URL, params=params, timeout=20)
        r.raise_for_status()

        items = _parse_rss_items(r.text)
        if not items:
            return [
                {
                    "ticker": "",
                    "title": "Yahoo RSS parse returned no items",
                    "summary": "Fallback to stub due to empty RSS parse result.",
                }
            ]

        out: list[dict[str, Any]] = []
        def _strip_html(s: str) -> str:
            # RSS descriptions/ titles often contain HTML entities and tags.
            # Keep this lightweight: remove tags, unescape entities.
            import html
            import re

            s = html.unescape(s or "")
            s = re.sub(r"<[^>]+>", " ", s)
            s = re.sub(r"\s+", " ", s).strip()
            return s


        for it in items[:25]:
            title = _strip_html((it.get("title") or "").strip())
            summary = _strip_html((it.get("summary") or "").strip())
            text = f"{title} {summary}".upper()


            ticker = ""
            for t in ticker_universe:
                if t in text:
                    ticker = t
                    break

            out.append(
                {
                    "ticker": ticker,
                    "title": title,
                    "summary": summary,
                    "url": (it.get("link") or ""),
                }
            )


        return out

    except Exception as e:
        # Return diagnostic to make trial runs debuggable.
        return [
            {
                "ticker": "",
                "title": "Yahoo RSS fetch failed",
                "summary": str(e),
            }
        ]

