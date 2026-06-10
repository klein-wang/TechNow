from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.config import settings
from src.reporting.schemas import SectorRecommendation


def recommend_from_sentiments(items: list[dict[str, Any]]) -> list[SectorRecommendation]:
    # Aggregate by sector
    scores_by_sector: dict[str, list[float]] = defaultdict(list)
    confidences_by_sector: dict[str, list[str]] = defaultdict(list)
    examples_by_sector: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for it in items:
        sector = it["sector"]
        scores_by_sector[sector].append(float(it["sentiment_score"]))
        confidences_by_sector[sector].append(it.get("confidence", "low"))
        examples_by_sector[sector].append(it)

    recommendations: list[SectorRecommendation] = []
    for sector in sorted(scores_by_sector.keys()):
        sector_scores = scores_by_sector[sector]
        agg = sum(sector_scores) / max(len(sector_scores), 1)

        # Confidence check: any low confidence -> potentially flag
        confs = confidences_by_sector[sector]
        confidence_flag = "low" in confs

        if agg > settings.accumulate_threshold:
            rec = "Accumulate"
        elif agg < settings.caution_threshold:
            rec = "Caution"
        else:
            rec = "Monitor"

        # Pick top bullish/bearish items for narrative
        sorted_items = sorted(examples_by_sector[sector], key=lambda x: x["sentiment_score"])
        bearish = sorted_items[:2][::-1]  # most negative first
        bullish = sorted_items[-2:][::-1]

        recommendations.append(
            SectorRecommendation(
                sector=sector,
                aggregate_sentiment=agg,
                recommendation=rec,
                confidence_flag=confidence_flag,
                bullish_stories=[(x["ticker"], x["key_catalyst"]) for x in bullish],
                bearish_stories=[(x["ticker"], x["key_catalyst"]) for x in bearish],
            )
        )

    return recommendations

