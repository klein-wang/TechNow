# TMU Sector Monitor Agent

Python backend that ingests TMU-related news (Yahoo placeholder), derives sentiment/catalysts (LLM placeholder), applies rule-based recommendation logic, and generates a daily `.txt` report.

## Quickstart

### 1) Create venv
```bat
py -m venv .venv
.\.venv\Scripts\activate
```

### 2) Install deps
```bat
pip install -e .
pip install ".[dev]"
```

### 3) Run once
```bat
python -m src.main --report-dir reports
```

### 4) Run scheduler (daily)
```bat
python -m src.main --schedule
```

## Notes
- Yahoo News integration is implemented as a **best-effort** placeholder using a lightweight endpoint pattern.
- The LLM sentiment extraction is currently a stub returning deterministic scores.
- Replace `src/nlp/sentiment_llm.py` with an actual LLM call when ready.

