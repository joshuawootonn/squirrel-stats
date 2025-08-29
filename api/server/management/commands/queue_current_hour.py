"""
Queues per-site aggregation jobs for the current hour.

Run this every minute via cron or a scheduler.
If RQ is available (REDIS_URL env), jobs are enqueued; otherwise falls back to direct call.
"""

import os
from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from server.models import Site

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
        # Enqueue manage.py command through RQ (simple approach: call command in worker)
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
    help = "Queue per-site aggregation for the current hour (run every minute)"

    def handle(self, *args, **options):
        now = timezone.now()
        current_hour_start = now.replace(minute=0, second=0, microsecond=0)
        current_hour_end = current_hour_start + timedelta(hours=1)

        for site in Site.objects.all().only("identifier"):
            _enqueue_or_run(site.identifier, current_hour_start, current_hour_end)

        self.stdout.write(self.style.SUCCESS("Queued/processed current-hour aggregation for all sites"))
