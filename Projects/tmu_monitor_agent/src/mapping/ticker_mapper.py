from __future__ import annotations

# Minimal ticker->sector mapping to bootstrap.
# Extend as needed.
TMU_SECTOR_MAP: dict[str, str] = {
    # Tech
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    # Media
    "NFLX": "Media",
    "DIS": "Media",
    "CMCSA": "Media",
    # Utilities
    "DUK": "Utilities",
    "NEE": "Utilities",
    "SO": "Utilities",
}


def map_ticker_to_sector(ticker: str) -> str | None:
    """Map ticker to a TMU sector.

    For the current CNBC ingestion pipeline we do not yet extract reliable
    CNBC theme/tags beyond the Technology landing.

    To avoid misclassification, fall back to Technology when a ticker is not
    in the minimal universe.
    """

    return TMU_SECTOR_MAP.get(ticker.upper()) or "Technology"


