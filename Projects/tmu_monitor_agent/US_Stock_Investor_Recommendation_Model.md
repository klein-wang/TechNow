# US Stock Investor Recommendation Model (Pivot)

## Goal
Build a US stock investor recommendation model that:
1) ingests price time series, fundamentals, and external market news/macros,
2) computes factor signals (momentum, quality, valuation, risk),
3) produces a final score and match label (strong/medium/low/neutral/avoid-wait/high risk),
4) optionally generates an LLM narrative summary with bull/bear/risks/watchlist.

This model must be added **alongside** the existing TMU monitor agent so the current pipeline remains intact until the new model can generate reports.

---

## Architecture (requested)
- `config: universe.yml`
- `data: market_data.py, fundamentals.py, news.py`
- `signals: momentum.py, quality.py, valuation.py, risk.py`
- `scoring: score.py`
- `reports: report.py`
- `alerts: alert_handling.py`
- `main.py` (new entrypoint for the US model)
- `llm/narrative.py` (LLM layer; prompt-first + deterministic fallback)

---

## Universe
- Mega-cap: AAPL, MSFT, GOOGL, META, AMZN
- Semiconductors: NVDA, AMD, AVGO, INTC, TSM, ASML
- Software/SaaS: CRM, NOW, ADBE, SNOW, ORCL, SAP, DDOG, CWD
- Benchmarks: QQQ, XLK, SMH

---

## Signal definitions
### Momentum signal
- 1-month return (~20 trading days)
- 3-month return (~60 trading days)
- price vs 50-day moving average
- price vs 100-day moving average

### Quality signal
- gross margin
- operating margin
- free cash flow margin

### Valuation signal
- P/E
- EV/Sales
- EV/EBITDA
- Free cash flow yield

### Risk signal
- volatility (annualized from rolling std dev of returns)
- regulatory risk (placeholder; derived from news topic extraction later)

---

## Scoring & labeling
- Compute normalized factor sub-scores.
- Weighted aggregation into a final score.
- Convert to labels:
  - strong / medium / low / neutral / avoid-wait
  - plus `high_risk` overlay if risk score exceeds threshold.

---

## LLM narrative prompt (prompt-first)
System/assistant behavior:
- "You are an investment research assistent. Given the following quantitative signals, summarize: 1. bull case, 2. bear case, 3. key risks, 4. further to be checked, stock watchlist etc."

Implementation detail:
- If no API key is configured, return deterministic narrative from templates.

---

## Run
From `Projects/tmu_monitor_agent`:
```bat
python -m src.main --report-dir reports
```
The initial implementation uses stubs so the pipeline runs end-to-end.

---

## Notes
- Data ingestion will be stubbed first. Replace stubs with real providers (e.g., yfinance/Polygon/FMP/SEC/LLM/news APIs) as next steps.

