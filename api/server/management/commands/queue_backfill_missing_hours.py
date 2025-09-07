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

from otel_config import get_tracer
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
    tracer = get_tracer()
    with tracer.start_as_current_span("enqueue_backfill_hourly_aggregation") as span:
        span.set_attribute("site.identifier", site_identifier)
        span.set_attribute("aggregation.start", start.isoformat())
        span.set_attribute("aggregation.end", end.isoformat())

        if redis_conn and Queue:
            span.set_attribute("execution.mode", "enqueued")
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
            span.set_attribute("execution.mode", "direct")
            call_command("aggregate_hourly_stats", site=site_identifier, start=start.isoformat(), end=end.isoformat())


class Command(BaseCommand):
    help = "Queue per-site backfill for missing hourly aggregations in the last 7 days (run hourly)"

    def handle(self, *args, **options):
        tracer = get_tracer()
        with tracer.start_as_current_span("queue_backfill_missing_hours_command") as span:
            now = timezone.now()
            start_window = (now - timedelta(days=7)).replace(minute=0, second=0, microsecond=0)
            end_window = now.replace(minute=0, second=0, microsecond=0)

            span.set_attribute("command.start_window", start_window.isoformat())
            span.set_attribute("command.end_window", end_window.isoformat())
            span.set_attribute("command.days_back", 7)

            sites = Site.objects.all().only("id", "identifier")
            site_count = sites.count()
            span.set_attribute("command.sites_count", site_count)

            total_missing_hours = 0

            # Iterate per site; for each hour in window, check if aggregation exists, if not queue
            for site in sites:
                site_missing_hours = 0
                current_hour = start_window
                while current_hour < end_window:
                    exists = HourlyPageViewStats.objects.filter(site=site, hour_bucket=current_hour).exists()
                    if not exists:
                        _enqueue_or_run(site.identifier, current_hour, current_hour + timedelta(hours=1))
                        site_missing_hours += 1
                        total_missing_hours += 1
                    current_hour += timedelta(hours=1)

                if site_missing_hours > 0:
                    span.set_attribute(f"site.{site.identifier}.missing_hours", site_missing_hours)

            span.set_attribute("command.total_missing_hours", total_missing_hours)

            self.stdout.write(self.style.SUCCESS("Queued/processed backfill for missing hours (last 7 days)"))
