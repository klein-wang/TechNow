from __future__ import annotations

import argparse
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from src.config import settings
from src.pipeline.run_agent import run_once
from src.reporting.report_generator import write_report


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--report-dir", default=settings.default_report_dir)
    p.add_argument("--schedule", action="store_true", help="Run as daily scheduler")
    return p


def schedule_job(report_dir: str) -> None:
    scheduler = BackgroundScheduler(timezone=settings.timezone)
    scheduler.add_job(
        lambda: run_and_write(report_dir),
        "cron",
        hour=settings.report_hour_local,
        minute=0,
        id="tmu_daily_job",
        replace_existing=True,
    )
    scheduler.start()
    print(f"Scheduler started (timezone={settings.timezone}). Job will run daily at {settings.report_hour_local:02d}:00.")

    try:
        while True:
            # keep process alive
            import time

            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


def run_and_write(report_dir: str) -> None:
    os.makedirs(report_dir, exist_ok=True)
    result = run_once()
    ts = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(report_dir, f"tmu_sector_report_{ts}.txt")
    write_report(result, out_path)
    print(f"Report written: {out_path}")


def main() -> None:
    args = build_arg_parser().parse_args()

    if args.schedule:
        schedule_job(args.report_dir)
        return

    os.makedirs(args.report_dir, exist_ok=True)
    result = run_once()
    ts = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(args.report_dir, f"tmu_sector_report_{ts}.txt")
    write_report(result, out_path)
    print(f"Report written: {out_path}")


if __name__ == "__main__":
    main()

