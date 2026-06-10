from __future__ import annotations

from typing import Any

from urllib.parse import urljoin

import requests




CNBC_TECH_BASE_URL = "https://www.cnbc.com/technology/"


def fetch_cnbc_technology_news(query: str | None = None) -> list[dict[str, Any]]:
    """Fetch CNBC Technology page and return best-effort items with real URLs.

    This version ports the DOM scraping logic from `CNBC_news/news_extract.py`.

    Output schema expected by the pipeline:
      [{"ticker": str, "title": str, "summary": str, "url": str}]

    Notes:
    - We still infer `ticker` via keyword matching because the scraping logic
      returns title/date/link rather than ticker-specific entities.
    - Sentiment extraction downstream uses `summary`/`title` text, so we
      provide a summary derived from the scraped title.
    """

    # Keep consistent with the rest of the project universe
    ticker_universe = ["AAPL", "MSFT", "NVDA", "NFLX", "DIS", "CMCSA", "DUK", "NEE", "SO"]

    # Import locally so the ingestion module doesn't hard-require pandas when the user
    # only wants to run other parts of the app.
    try:
        from CNBC_news.news_extract import extract_sections, extract_cnbc_articles
    except Exception as e:  # pragma: no cover
        # Hard failure: return empty list rather than placeholder so downstream can
        # decide what to do.
        return []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }


    try:
        # First crawl the technology landing page to discover subsections.
        # Prefer DOM-based section extraction; it's already implemented in CNBC_news.
        # Note: the original CNBC_news implementation requests without custom headers.
        sections_df = extract_sections(CNBC_TECH_BASE_URL)

        if sections_df is None or sections_df.empty:
            return []

        # Only crawl a handful of subsections to avoid huge runtime.
        max_sections = 6
        max_articles_total = 50
        out: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for i in range(min(max_sections, len(sections_df))):
            # sections_df columns are: ['Section', 'link']
            rel_or_abs = str(sections_df.iloc[i][1])
            if not rel_or_abs:
                continue

            section_url = urljoin(CNBC_TECH_BASE_URL, rel_or_abs)

            df_section = extract_cnbc_articles(section_url, str(sections_df.iloc[i][0]))
            if df_section is None or df_section.empty:
                continue

            # Ensure we iterate newest-first; news_extract.py already sorts by date
            for _, row in df_section.iterrows():
                link = str(row.get("link") or "").strip()
                if not link or link in seen_urls:
                    continue

                # Some links might still be relative; normalize
                link_abs = urljoin(CNBC_TECH_BASE_URL, link)
                seen_urls.add(link_abs)

                title = str(row.get("title") or "").strip()
                # news_extract.py often appends ';' to title fragments; clean it.
                title = title.replace(";", "").strip()
                date = str(row.get("date") or "").strip()

                summary = title
                # add date into summary to give the downstream sentiment stub more context
                if date and date != "NA":
                    summary = f"{title} ({date})".strip()

                upper = f"{title} {summary}".upper()
                ticker = ""
                for t in ticker_universe:
                    if t in upper:
                        ticker = t
                        break

                # If we can't infer ticker, skip (pipeline would skip anyway)
                if not ticker:
                    continue

                out.append(
                    {
                        "ticker": ticker,
                        "title": title,
                        "summary": summary,
                        "url": link_abs,
                    }
                )

                if len(out) >= max_articles_total:
                    return out

        return out

    except requests.RequestException:
        return []
    except Exception:
        return []


