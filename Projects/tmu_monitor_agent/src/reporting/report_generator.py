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
        lines.append(
            f"Top sector by sentiment: {best.sector} ({best.recommendation}) [agg={best.aggregate_sentiment:.2f}]"
        )
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
            url = next((u.get("url") for u in result.items if u.get("ticker") == tkr and u.get("url")), "")
            lines.append(f"  • {tkr}: {cat}")
            if url:
                lines.append(f"    URL: {url}")

        lines.append(f"{r.sector} - Bearish")
        for tkr, cat in r.bearish_stories:
            url = next(
                (
                    u.get("url")
                    for u in result.items
                    if u.get("ticker") == tkr and u.get("url")
                ),
                "",
            )
            title = next(
                (
                    u.get("title")
                    for u in result.items
                    if u.get("ticker") == tkr and u.get("title")
                ),
                "",
            )
            lines.append(f"  • {tkr}: {cat}")
            if title:
                lines.append(f"    Title: {title}")
            if url:
                lines.append(f"    URL: {url}")

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

    # Holistic appendix: all ingested (scraped) & mapped articles
    lines.append("\nALL INGESTED ARTICLES")
    lines.append("----------------------")

    for it in sorted(
        result.items,
        key=lambda x: (
            x.get("sector", ""),
            x.get("ticker", ""),
            x.get("date", ""),
            x.get("url", ""),
        ),
    ):
        tkr = it.get("ticker") or ""
        sector = it.get("sector") or ""
        title = it.get("title") or ""
        summary = it.get("summary") or ""
        url = it.get("url") or ""

        lines.append(f"[{sector}] {tkr}")
        if title:
            lines.append(f"  Title: {title}")
        if summary:
            lines.append(f"  Summary: {summary}")
        if url:
            lines.append(f"  URL: {url}")
        lines.append("  " + "-" * 40)

    content = "\n".join(lines).rstrip() + "\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

