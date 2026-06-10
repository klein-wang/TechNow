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
    return TMU_SECTOR_MAP.get(ticker.upper())

