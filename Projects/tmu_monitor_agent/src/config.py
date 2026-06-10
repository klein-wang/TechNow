from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Scheduler
    report_hour_local: int = 8  # 08:00
    timezone: str = "US/Eastern"

    # Output
    default_report_dir: str = "reports"

    # Thresholds (per design doc)
    accumulate_threshold: float = 0.7
    caution_threshold: float = -0.5


settings = Settings()

