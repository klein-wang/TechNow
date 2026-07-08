# TODO

## Completed
- Run US Stock Investor Recommendation Model report (today) -> `reports/us_investor_recommendations_2026-07-08.txt`

## Next
- Add auditability artifacts:
  - Create a per-run folder under `reports/us_model_runs/<YYYY-MM-DD>/`
  - Persist the last 10 days of price closes per ticker
  - Persist internal calculation inputs/outputs per ticker:
    - momentum signals (ret_20d, ret_60d, price_to_ma_50d, price_to_ma_100d)
    - quality signals (gross/operating/FCF margins)
    - valuation signals (pe, ev_to_sales, ev_to_ebitda, fcf_yield)
    - risk signals (volatility_60d_ann, regulatory_risk_score)
    - final normalized factor percentiles (momentum/quality/valuation/risk)
    - final score, label, risk_flags
  - Store the same data as JSON (machine-readable) and optionally a human-readable text appendix.
- Update `src/scoring/score.py` to return extra audit data (raw factors + percentiles) without breaking existing API.
- Update `src/main.py` to write audit artifacts alongside the report.

