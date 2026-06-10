from __future__ import annotations

from src.mapping.ticker_mapper import map_ticker_to_sector


def test_ticker_mapping():
    assert map_ticker_to_sector("AAPL") == "Technology"
    assert map_ticker_to_sector("nflx") == "Media"
    assert map_ticker_to_sector("UNKNOWN") is None

