from __future__ import annotations

from src.recommendation.logic import recommend_from_sentiments


def test_recommendation_thresholds():
    items = [
        {"sector": "Technology", "ticker": "AAPL", "sentiment_score": 0.8, "confidence": "high", "key_catalyst": "x"},
        {"sector": "Technology", "ticker": "MSFT", "sentiment_score": 0.9, "confidence": "high", "key_catalyst": "y"},
        {"sector": "Utilities", "ticker": "DUK", "sentiment_score": -0.6, "confidence": "low", "key_catalyst": "z"},
    ]

    recs = recommend_from_sentiments(items)
    tech = [r for r in recs if r.sector == "Technology"][0]
    util = [r for r in recs if r.sector == "Utilities"][0]

    assert tech.recommendation == "Accumulate"
    assert util.recommendation == "Caution"
    assert util.confidence_flag is True

