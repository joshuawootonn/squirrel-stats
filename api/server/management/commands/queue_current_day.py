"""
Queues per-site daily aggregation jobs for the current day.

Run this once per day via cron or a scheduler.
If RQ is available (REDIS_URL env), jobs are enqueued; otherwise falls back to direct call.
"""

import os
from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from otel_config import get_tracer
from server.models import Site

try:
    import redis  # type: ignore
    from rq import Queue  # type: ignore

    REDIS_URL = os.getenv("REDIS_URL")
    redis_conn = redis.from_url(REDIS_URL) if REDIS_URL else None
except Exception:  # pragma: no cover
    redis_conn = None
    Queue = None  # type: ignore


def _enqueue_or_run(site_identifier: str, start_date, end_date):
    tracer = get_tracer()
    with tracer.start_as_current_span("enqueue_daily_aggregation") as span:
        span.set_attribute("site.identifier", site_identifier)
        span.set_attribute("aggregation.start", start_date.isoformat())
        span.set_attribute("aggregation.end", end_date.isoformat())

        if redis_conn and Queue:
            span.set_attribute("execution.mode", "enqueued")
            q = Queue("aggregations", connection=redis_conn)
            # Enqueue manage.py command through RQ (simple approach: call command in worker)
            q.enqueue(
                call_command,
                "aggregate_daily_stats",
                "--site",
                site_identifier,
                "--start",
                start_date.isoformat(),
                "--end",
                end_date.isoformat(),
            )
        else:
            span.set_attribute("execution.mode", "direct")
            call_command(
                "aggregate_daily_stats", site=site_identifier, start=start_date.isoformat(), end=end_date.isoformat()
            )


class Command(BaseCommand):
    help = "Queue per-site aggregation for the current day (run once daily)"

    def handle(self, *args, **options):
        tracer = get_tracer()
        with tracer.start_as_current_span("queue_current_day_command") as span:
            now = timezone.now()
            current_day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            current_day_end = current_day_start + timedelta(days=1)

            span.set_attribute("command.day_start", current_day_start.isoformat())
            span.set_attribute("command.day_end", current_day_end.isoformat())

            sites = Site.objects.all().only("identifier")
            site_count = sites.count()
            span.set_attribute("command.sites_count", site_count)

            for site in sites:
                _enqueue_or_run(site.identifier, current_day_start.date(), current_day_end.date())

            self.stdout.write(self.style.SUCCESS("Queued/processed current-day aggregation for all sites"))
