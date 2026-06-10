from __future__ import annotations

import os
import tempfile

from src.reporting.report_generator import write_report
from src.reporting.schemas import AgentRunResult, SectorRecommendation


def test_report_written():
    rec = SectorRecommendation(
        sector="Technology",
        aggregate_sentiment=0.8,
        recommendation="Accumulate",
        confidence_flag=False,
        bullish_stories=[("AAPL", "x")],
        bearish_stories=[("MSFT", "y")],
    )
    result = AgentRunResult(items=[], recommendations=[rec])

    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "out.txt")
        write_report(result, p)
        assert os.path.exists(p)
        with open(p, "r", encoding="utf-8") as f:
            s = f.read()
        assert "TMU Sector Monitor" in s
        assert "Technology" in s

