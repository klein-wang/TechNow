# TODO

## CNBC ingestion logic revision
- [ ] Step 1: Inspect current ingestion implementation (`src/ingestion/cnbc_technology_news.py`) and CNBC_news extraction functions.
- [ ] Step 2: Update `src/ingestion/cnbc_technology_news.py` to fetch `https://www.cnbc.com/technology/` and extract real article URLs using the CNBC_news DOM logic.
- [ ] Step 3: Ensure URL joining is robust (use `urllib.parse.urljoin`).
- [ ] Step 4: Keep output schema compatible with pipeline: `{ticker, title, summary, url}`.
- [ ] Step 5: Add limits/timeouts and robust error handling; return empty list on failure.
- [ ] Step 6: Run `python -m src.main --report-dir reports` and sanity-check that generated report includes URLs.

