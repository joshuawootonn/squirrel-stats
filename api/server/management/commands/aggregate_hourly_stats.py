"""
Django management command to aggregate pageview data into hourly statistics.

This command processes raw PageView records and creates/updates HourlyPageViewStats
records for efficient analytics queries. Designed to be run via cron job.

Usage:
    python manage.py aggregate_hourly_stats [--hours=N] [--site=identifier]

Options:
    --hours=N: Process the last N hours (default: 24)
    --site=identifier: Process only the specified site (default: all sites)
"""

import logging
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from otel_config import get_tracer
from server.models import HourlyPageViewStats, PageView, Site

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Aggregate pageview data into hourly statistics for analytics"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Number of hours to process (default: 24)",
        )
        parser.add_argument(
            "--start",
            type=str,
            help="ISO8601 start datetime (UTC). If provided, overrides --hours range start.",
        )
        parser.add_argument(
            "--end",
            type=str,
            help="ISO8601 end datetime (UTC). If provided, overrides --hours range end.",
        )
        parser.add_argument(
            "--site",
            type=str,
            help="Site identifier to process (default: all sites)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )

    def handle(self, *args, **options):
        tracer = get_tracer()
        with tracer.start_as_current_span("aggregate_hourly_stats_command") as span:
            hours_to_process = options["hours"]
            start_str = options.get("start")
            end_str = options.get("end")
            site_identifier = options.get("site")
            verbose = options.get("verbose", False)

            # Set span attributes for observability
            span.set_attribute("command.hours_to_process", hours_to_process)
            if start_str:
                span.set_attribute("command.start_str", start_str)
            if end_str:
                span.set_attribute("command.end_str", end_str)
            if site_identifier:
                span.set_attribute("command.site_identifier", site_identifier)

            if verbose:
                logger.setLevel(logging.DEBUG)

            self.stdout.write(self.style.SUCCESS(f"Starting hourly aggregation for last {hours_to_process} hours..."))

            # Calculate time range to process
            if start_str or end_str:
                # Parse explicit start/end if provided
                try:
                    if start_str:
                        start_time = datetime.fromisoformat(start_str)
                        if start_time.tzinfo is None:
                            start_time = timezone.make_aware(start_time, timezone.utc)
                    else:
                        start_time = None
                    if end_str:
                        end_time = datetime.fromisoformat(end_str)
                        if end_time.tzinfo is None:
                            end_time = timezone.make_aware(end_time, timezone.utc)
                    else:
                        end_time = None
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Invalid --start/--end datetime: {e}"))
                    return

                # Defaults if only one bound provided
                if start_time is None:
                    end_time = end_time or timezone.now()
                    start_time = end_time - timedelta(hours=hours_to_process)
                if end_time is None:
                    start_time = start_time
                    end_time = start_time + timedelta(hours=hours_to_process)
            else:
                end_time = timezone.now()
                start_time = end_time - timedelta(hours=hours_to_process)

            # Get sites to process
            sites_query = Site.objects.all()
            if site_identifier:
                try:
                    sites_query = sites_query.filter(identifier=site_identifier)
                    if not sites_query.exists():
                        self.stdout.write(self.style.ERROR(f"Site '{site_identifier}' not found"))
                        return
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error filtering sites: {e}"))
                    return

            total_processed = 0
            total_created = 0
            total_updated = 0

            for site in sites_query:
                try:
                    created, updated, processed = self._process_site_hours(site, start_time, end_time, verbose)
                    total_created += created
                    total_updated += updated
                    total_processed += processed

                    if verbose:
                        self.stdout.write(
                            f"Site {site.identifier}: {created} created, {updated} updated, {processed} pageviews processed"
                        )

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing site {site.identifier}: {e}"))
                    logger.exception(f"Error processing site {site.identifier}")

            # Set final span attributes
            span.set_attribute("command.total_created", total_created)
            span.set_attribute("command.total_updated", total_updated)
            span.set_attribute("command.total_processed", total_processed)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Completed: {total_created} records created, {total_updated} updated, {total_processed} pageviews processed"
                )
            )

    def _process_site_hours(
        self, site: Site, start_time: datetime, end_time: datetime, verbose: bool
    ) -> tuple[int, int, int]:
        """
        Process hourly aggregations for a single site within the time range.

        Returns:
            tuple: (created_count, updated_count, processed_pageviews_count)
        """
        created_count = 0
        updated_count = 0
        processed_pageviews = 0

        # Generate all hour buckets in the range
        current_hour = self._truncate_to_hour(start_time)
        end_hour = self._truncate_to_hour(end_time)

        while current_hour <= end_hour:
            next_hour = current_hour + timedelta(hours=1)

            try:
                with transaction.atomic():
                    # Get or create the hourly stats record
                    hourly_stats, created = HourlyPageViewStats.objects.get_or_create(
                        site=site,
                        hour_bucket=current_hour,
                        defaults={
                            "pageview_count": 0,
                            "unique_session_count": 0,
                        },
                    )

                    # Find pageviews in this hour that haven't been processed yet
                    pageviews_query = PageView.objects.filter(
                        site=site,
                        created_at__gte=current_hour,
                        created_at__lt=next_hour,
                    )

                    # If this is an update, only process new pageviews
                    if not created and hourly_stats.last_processed_pageview_id:
                        pageviews_query = pageviews_query.filter(
                            created_at__gt=PageView.objects.get(id=hourly_stats.last_processed_pageview_id).created_at
                        )

                    pageviews = list(pageviews_query.order_by("created_at"))

                    if pageviews:
                        # Count total pageviews
                        new_pageview_count = len(pageviews)

                        # Count unique sessions
                        session_ids = set()
                        for pv in pageviews:
                            if pv.session:
                                session_ids.add(pv.session.id)

                        # Update the aggregation
                        if created:
                            hourly_stats.pageview_count = new_pageview_count
                            hourly_stats.unique_session_count = len(session_ids)
                        else:
                            hourly_stats.pageview_count += new_pageview_count
                            # For unique sessions, we need to recalculate to avoid double-counting
                            all_sessions = (
                                PageView.objects.filter(
                                    site=site,
                                    created_at__gte=current_hour,
                                    created_at__lt=next_hour,
                                    session__isnull=False,
                                )
                                .values_list("session", flat=True)
                                .distinct()
                            )
                            hourly_stats.unique_session_count = len(list(all_sessions))

                        # Track the last processed pageview
                        hourly_stats.last_processed_pageview_id = pageviews[-1].id
                        hourly_stats.save()

                        processed_pageviews += new_pageview_count

                        if verbose:
                            self.stdout.write(
                                f"  {current_hour}: {new_pageview_count} pageviews, {len(session_ids)} sessions"
                            )

                    if created:
                        created_count += 1
                    elif pageviews:  # Only count as updated if we actually processed new data
                        updated_count += 1

            except Exception as e:
                logger.exception(f"Error processing hour {current_hour} for site {site.identifier}")
                self.stdout.write(self.style.ERROR(f"Error processing {current_hour} for {site.identifier}: {e}"))

            current_hour = next_hour

        return created_count, updated_count, processed_pageviews

    def _truncate_to_hour(self, dt: datetime) -> datetime:
        """Truncate datetime to the beginning of the hour (UTC)."""
        return dt.replace(minute=0, second=0, microsecond=0)
