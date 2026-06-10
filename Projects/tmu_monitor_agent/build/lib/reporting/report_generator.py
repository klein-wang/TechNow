from __future__ import annotations

from src.reporting.schemas import AgentRunResult


def write_report(result: AgentRunResult, out_path: str) -> None:
    lines: list[str] = []

    lines.append("TMU Sector Monitor - Daily Report")
    lines.append("=" * 40)

    # Executive summary
    lines.append("\nEXECUTIVE SUMMARY")
    lines.append("-------------------")
    top = sorted(result.recommendations, key=lambda r: r.aggregate_sentiment, reverse=True)
    if top:
        best = top[0]
        lines.append(f"Top sector by sentiment: {best.sector} ({best.recommendation}) [agg={best.aggregate_sentiment:.2f}]")
    else:
        lines.append("No sector data available for today.")

    # Sector breakdown
    lines.append("\nSECTOR BREAKDOWN")
    lines.append("----------------")
    for r in result.recommendations:
        flag = " (LOW CONFIDENCE)" if r.confidence_flag else ""
        lines.append(f"- {r.sector}: {r.recommendation} [agg={r.aggregate_sentiment:.2f}]{flag}")

    # Top stories
    lines.append("\nTOP STORIES")
    lines.append("-----------")
    for r in result.recommendations:
        lines.append(f"\n{r.sector} - Bullish")
        for tkr, cat in r.bullish_stories:
            lines.append(f"  • {tkr}: {cat}")
        lines.append(f"{r.sector} - Bearish")
        for tkr, cat in r.bearish_stories:
            lines.append(f"  • {tkr}: {cat}")

    # Specific recommendations
    lines.append("\nRECOMMENDATIONS")
    lines.append("-----------------")
    for r in result.recommendations:
        lines.append(f"\n{r.sector}: {r.recommendation}")
        lines.append("  Rationale:")
        lines.append(f"    Aggregate sentiment: {r.aggregate_sentiment:.2f}")
        if r.confidence_flag:
            lines.append("    Confidence check: Flagged for human review.")
        lines.append("    Bullish catalysts:")
        for _, cat in r.bullish_stories:
            lines.append(f"      - {cat}")
        lines.append("    Bearish catalysts:")
        for _, cat in r.bearish_stories:
            lines.append(f"      - {cat}")

    content = "\n".join(lines).rstrip() + "\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

