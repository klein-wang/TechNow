from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import os


DEFAULT_SYSTEM_PROMPT = """You are an investment research assistent."""  # keep original typo for compatibility

DEFAULT_USER_PROMPT_TEMPLATE = """
Given the following quantitative signals for {ticker}:
- score: {score}
- label: {label}
- factors: {factors}

Summarize:
1. bull case
2. bear case
3. key risks
4. further to be checked
5. stock watchlist / catalysts to monitor

Keep it concise (bullet points).
""".strip()


def generate_narrative(
    *,
    ticker: str,
    score: float,
    label: str,
    factors: Dict[str, float],
    api_key_env: str = "OPENAI_API_KEY",
) -> Dict[str, Any]:
    """LLM narrative layer.

    Deterministic fallback if no API key is present.

    Later: integrate real model calls.
    """

    api_key = os.getenv(api_key_env, "").strip()
    prompt = DEFAULT_USER_PROMPT_TEMPLATE.format(ticker=ticker, score=score, label=label, factors=factors)

    # deterministic fallback
    if not api_key:
        bull = []
        bear = []
        risks = []
        further = []
        watch = []

        if factors.get("momentum", 0.5) >= 0.6:
            bull.append("Price momentum is favorable across recent windows.")
            watch.append("Recent earnings revisions / guidance changes.")
        else:
            bear.append("Momentum is neutral-to-weak versus benchmarks.")
            watch.append("Relative strength vs QQQ/XLK (trend confirmation).")

        if factors.get("quality", 0.5) >= 0.6:
            bull.append("Margins and free-cash-flow characteristics look supportive.")
        else:
            bear.append("Quality metrics are not compelling versus peers.")

        if factors.get("valuation", 0.5) >= 0.6:
            bull.append("Valuation is attractive on multiples / FCF yield proxy.")
        else:
            bear.append("Valuation offers less support (higher multiples / lower yield proxy).")

        if label == "high risk" or factors.get("risk", 0.5) < 0.4:
            risks.append("Higher volatility / regulatory overhang risk profile.")
            further.append("Validate regulatory exposure and near-term event calendar.")
            further.append("Check drawdown behavior under market stress.")
        else:
            risks.append("Monitor macro/interest-rate sensitivity." )
            further.append("Confirm factor stability over the next 1-2 rebalances.")

        return {
            "input_prompt": prompt,
            "bull_case": bull or ["Qualitative outlook depends on catalysts and factor continuation."],
            "bear_case": bear or ["Downside could emerge if macro conditions tighten."],
            "key_risks": risks or ["Liquidity and volatility could increase around earnings."] ,
            "further_to_be_checked": further or ["Cross-check with earnings, guidance, and balance sheet trends."],
            "watchlist": watch or ["Track earnings, macro data releases, and sector headlines."],
            "llm_provider": None,
        }

    # If API key exists, a real integration would go here.
    # Keep stub to avoid accidental live calls.
    return {
        "input_prompt": prompt,
        "bull_case": ["(LLM integration pending)"],
        "bear_case": ["(LLM integration pending)"],
        "key_risks": ["(LLM integration pending)"],
        "further_to_be_checked": ["(LLM integration pending)"],
        "watchlist": ["(LLM integration pending)"],
        "llm_provider": api_key_env,
    }

