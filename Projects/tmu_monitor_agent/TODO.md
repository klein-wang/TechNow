# TODO

## Pivot: US Stock Investor Recommendation Model (alongside existing TMU monitor)

- [ ] Step 1: Add configuration + universe definition: `config/universe.yml`
- [ ] Step 2: Create ingestion layer stubs/modules: `src/data/market_data.py`, `src/data/fundamentals.py`, `src/data/news.py`
- [ ] Step 3: Create signal modules: `src/signals/momentum.py`, `src/signals/quality.py`, `src/signals/valuation.py`, `src/signals/risk.py`
- [ ] Step 4: Create scoring/labeling: `src/scoring/score.py`
- [ ] Step 5: Create reporting + alerting: `src/reports/report.py`, `src/alerts/alert_handling.py`
- [ ] Step 6: Create LLM narrative adapter (prompt-first) with deterministic fallback: `src/llm/narrative.py`
- [x] Step 7: Add model entrypoint: `src/main.py` (new, non-breaking to current TMU)
- [x] Step 8: Add documentation: `US_Stock_Investor_Recommendation_Model.md`
- [x] Step 9: Run `python -m src.main --report-dir reports` to generate a first report (using stubs)


