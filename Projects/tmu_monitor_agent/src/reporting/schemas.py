from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SectorRecommendation:
    sector: str
    aggregate_sentiment: float
    recommendation: str
    confidence_flag: bool
    bullish_stories: list[tuple[str, str]]
    bearish_stories: list[tuple[str, str]]


@dataclass
class AgentRunResult:
    items: list[dict[str, Any]]
    recommendations: list[SectorRecommendation]

