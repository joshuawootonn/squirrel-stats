"""
Queues per-site backfill aggregation for any missing hours in the last 7 days.

Run this hourly. Enqueues specific hour windows that have no aggregation record.
Falls back to direct execution if RQ/Redis is not available.
"""

import os
from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from server.models import HourlyPageViewStats, Site

try:
    import redis  # type: ignore
    from rq import Queue  # type: ignore

    REDIS_URL = os.getenv("REDIS_URL")
    redis_conn = redis.from_url(REDIS_URL) if REDIS_URL else None
except Exception:  # pragma: no cover
    redis_conn = None
    Queue = None  # type: ignore


def _enqueue_or_run(site_identifier: str, start, end):
    if redis_conn and Queue:
        q = Queue("aggregations", connection=redis_conn)
        q.enqueue(
            call_command,
            "aggregate_hourly_stats",
            "--site",
            site_identifier,
            "--start",
            start.isoformat(),
            "--end",
            end.isoformat(),
        )
    else:
        call_command("aggregate_hourly_stats", site=site_identifier, start=start.isoformat(), end=end.isoformat())


class Command(BaseCommand):
    help = "Queue per-site backfill for missing hourly aggregations in the last 7 days (run hourly)"

    def handle(self, *args, **options):
        now = timezone.now()
        start_window = (now - timedelta(days=7)).replace(minute=0, second=0, microsecond=0)
        end_window = now.replace(minute=0, second=0, microsecond=0)

        # Iterate per site; for each hour in window, check if aggregation exists, if not queue
        for site in Site.objects.all().only("id", "identifier"):
            current_hour = start_window
            while current_hour < end_window:
                exists = HourlyPageViewStats.objects.filter(site=site, hour_bucket=current_hour).exists()
                if not exists:
                    _enqueue_or_run(site.identifier, current_hour, current_hour + timedelta(hours=1))
                current_hour += timedelta(hours=1)

        self.stdout.write(self.style.SUCCESS("Queued/processed backfill for missing hours (last 7 days)"))
