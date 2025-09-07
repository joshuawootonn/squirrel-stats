"""
Queues backfill jobs for missing daily aggregations.

This command identifies days that are missing daily statistics and queues
them for processing. Useful for ensuring data completeness after system
downtime or when adding new sites.

Usage:
    python manage.py queue_backfill_missing_days [--days=N]
"""

import os
from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from otel_config import get_tracer
from server.models import DailyPageViewStats, Site

try:
    import redis  # type: ignore
    from rq import Queue  # type: ignore

    REDIS_URL = os.getenv("REDIS_URL")
    redis_conn = redis.from_url(REDIS_URL) if REDIS_URL else None
except Exception:  # pragma: no cover
    redis_conn = None
    Queue = None  # type: ignore


def _enqueue_or_run(site_identifier: str, start_date, end_date):
    """Enqueue or directly run daily aggregation based on RQ availability."""
    tracer = get_tracer()
    with tracer.start_as_current_span("enqueue_backfill_daily_aggregation") as span:
        span.set_attribute("site.identifier", site_identifier)
        span.set_attribute("aggregation.start", start_date.isoformat())
        span.set_attribute("aggregation.end", end_date.isoformat())
        span.set_attribute("aggregation.days_count", (end_date - start_date).days + 1)

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
    help = "Queue backfill for missing daily aggregations (last 30 days by default)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days to check for missing data (default: 30)",
        )

    def handle(self, *args, **options):
        tracer = get_tracer()
        with tracer.start_as_current_span("queue_backfill_missing_days_command") as span:
            days_to_check = options["days"]
            now = timezone.now()
            end_date = now.date()
            start_date = end_date - timedelta(days=days_to_check)

            span.set_attribute("command.days_to_check", days_to_check)
            span.set_attribute("command.start_date", start_date.isoformat())
            span.set_attribute("command.end_date", end_date.isoformat())

            sites = Site.objects.all()
            site_count = sites.count()
            span.set_attribute("command.sites_count", site_count)

            total_queued = 0

            for site in sites:
                # Find existing daily stats for this site in the date range
                existing_days = set(
                    DailyPageViewStats.objects.filter(
                        site=site,
                        day_bucket__gte=start_date,
                        day_bucket__lte=end_date,
                    ).values_list("day_bucket", flat=True)
                )

                # Generate all days in the range and find missing ones
                current_date = start_date
                missing_days = []

                while current_date <= end_date:
                    if current_date not in existing_days:
                        missing_days.append(current_date)
                    current_date += timedelta(days=1)

                # Queue missing days for processing
                if missing_days:
                    # Group consecutive days for efficient processing
                    day_ranges = self._group_consecutive_days(missing_days)

                    for range_start, range_end in day_ranges:
                        _enqueue_or_run(site.identifier, range_start, range_end)
                        total_queued += (range_end - range_start).days + 1

                    span.set_attribute(f"site.{site.identifier}.missing_days", len(missing_days))
                    self.stdout.write(f"Site {site.identifier}: queued {len(missing_days)} missing days")

            span.set_attribute("command.total_queued", total_queued)

            self.stdout.write(self.style.SUCCESS(f"Queued/processed backfill for {total_queued} missing days"))

    def _group_consecutive_days(self, days):
        """
        Group consecutive days into ranges for efficient batch processing.

        Args:
            days: List of date objects

        Returns:
            List of (start_date, end_date) tuples
        """
        if not days:
            return []

        days = sorted(days)
        ranges = []
        range_start = days[0]
        range_end = days[0]

        for i in range(1, len(days)):
            if days[i] == range_end + timedelta(days=1):
                # Consecutive day, extend the range
                range_end = days[i]
            else:
                # Gap found, close current range and start new one
                ranges.append((range_start, range_end))
                range_start = days[i]
                range_end = days[i]

        # Add the final range
        ranges.append((range_start, range_end))

        return ranges
