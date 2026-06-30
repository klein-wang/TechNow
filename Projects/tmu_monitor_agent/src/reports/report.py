from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from src.scoring.score import TickerRecommendation


def build_text_report(
    *,
    recommendations: List[TickerRecommendation],
    report_title: str = "US Stock Investor Recommendation Report",
) -> str:
    lines: List[str] = []
    lines.append(report_title)
    lines.append("=" * len(report_title))

    lines.append("")
    lines.append("Top picks")
    lines.append("----------")

    top = recommendations[:10]
    for r in top:
        lines.append(
            f"{r.ticker}: score={r.score:.3f} label={r.label} factors={{m:{r.factors['momentum']:.2f}, q:{r.factors['quality']:.2f}, v:{r.factors['valuation']:.2f}, r:{r.factors['risk']:.2f}}}"
        )

    lines.append("")
    lines.append("All recommendations")
    lines.append("---------------------")
    for r in recommendations:
        lines.append(f"{r.ticker} | {r.label} | {r.score:.3f} | flags={','.join(r.risk_flags) if r.risk_flags else '-'}")

    # optional narrative would be appended by main
    return "\n".join(lines)

