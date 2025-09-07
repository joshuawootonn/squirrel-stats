"""
Django management command to aggregate pageview data into daily statistics.

This command processes raw PageView records and creates/updates DailyPageViewStats
records for efficient analytics queries. Designed to be run via cron job.

Usage:
    python manage.py aggregate_daily_stats [--days=N] [--site=identifier]

Options:
    --days=N: Process the last N days (default: 30)
    --site=identifier: Process only the specified site (default: all sites)
"""

import logging
from datetime import UTC, datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from otel_config import get_tracer
from server.models import DailyPageViewStats, PageView, Site

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Aggregate pageview data into daily statistics for analytics"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days to process (default: 30)",
        )
        parser.add_argument(
            "--start",
            type=str,
            help="ISO8601 start date (UTC). If provided, overrides --days range start.",
        )
        parser.add_argument(
            "--end",
            type=str,
            help="ISO8601 end date (UTC). If provided, overrides --days range end.",
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
        with tracer.start_as_current_span("aggregate_daily_stats_command") as span:
            days_to_process = options["days"]
            start_str = options.get("start")
            end_str = options.get("end")
            site_identifier = options.get("site")
            verbose = options.get("verbose", False)

            # Set span attributes for observability
            span.set_attribute("command.days_to_process", days_to_process)
            if start_str:
                span.set_attribute("command.start_str", start_str)
            if end_str:
                span.set_attribute("command.end_str", end_str)
            if site_identifier:
                span.set_attribute("command.site_identifier", site_identifier)

            if verbose:
                logger.setLevel(logging.DEBUG)

            self.stdout.write(self.style.SUCCESS(f"Starting daily aggregation for last {days_to_process} days..."))

            # Calculate time range to process
            if start_str or end_str:
                # Parse explicit start/end if provided
                try:
                    if start_str:
                        start_date = datetime.fromisoformat(start_str).date()
                    else:
                        start_date = None
                    if end_str:
                        end_date = datetime.fromisoformat(end_str).date()
                    else:
                        end_date = None
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Invalid --start/--end date: {e}"))
                    return

                # Defaults if only one bound provided
                if start_date is None:
                    end_date = end_date or timezone.now().date()
                    start_date = end_date - timedelta(days=days_to_process)
                if end_date is None:
                    start_date = start_date
                    end_date = start_date + timedelta(days=days_to_process)
            else:
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=days_to_process)

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
                    created, updated, processed = self._process_site_days(site, start_date, end_date, verbose)
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

    def _process_site_days(self, site: Site, start_date, end_date, verbose: bool) -> tuple[int, int, int]:
        """
        Process daily aggregations for a single site within the date range.

        Returns:
            tuple: (created_count, updated_count, processed_pageviews_count)
        """
        created_count = 0
        updated_count = 0
        processed_pageviews = 0

        # Generate all day buckets in the range
        current_date = start_date

        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)

            # Convert dates to datetime for querying PageView records
            day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()), UTC)
            day_end = timezone.make_aware(datetime.combine(next_date, datetime.min.time()), UTC)

            try:
                with transaction.atomic():
                    # Get or create the daily stats record
                    daily_stats, created = DailyPageViewStats.objects.get_or_create(
                        site=site,
                        day_bucket=current_date,
                        defaults={
                            "pageview_count": 0,
                            "unique_session_count": 0,
                        },
                    )

                    # Find pageviews in this day that haven't been processed yet
                    pageviews_query = PageView.objects.filter(
                        site=site,
                        created_at__gte=day_start,
                        created_at__lt=day_end,
                    )

                    # If this is an update, only process new pageviews
                    if not created and daily_stats.last_processed_pageview_id:
                        pageviews_query = pageviews_query.filter(
                            created_at__gt=PageView.objects.get(id=daily_stats.last_processed_pageview_id).created_at
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
                            daily_stats.pageview_count = new_pageview_count
                            daily_stats.unique_session_count = len(session_ids)
                        else:
                            daily_stats.pageview_count += new_pageview_count
                            # For unique sessions, we need to recalculate to avoid double-counting
                            all_sessions = (
                                PageView.objects.filter(
                                    site=site,
                                    created_at__gte=day_start,
                                    created_at__lt=day_end,
                                    session__isnull=False,
                                )
                                .values_list("session", flat=True)
                                .distinct()
                            )
                            daily_stats.unique_session_count = len(list(all_sessions))

                        # Track the last processed pageview
                        daily_stats.last_processed_pageview_id = pageviews[-1].id
                        daily_stats.save()

                        processed_pageviews += new_pageview_count

                        if verbose:
                            self.stdout.write(
                                f"  {current_date}: {new_pageview_count} pageviews, {len(session_ids)} sessions"
                            )

                    if created:
                        created_count += 1
                    elif pageviews:  # Only count as updated if we actually processed new data
                        updated_count += 1

            except Exception as e:
                logger.exception(f"Error processing day {current_date} for site {site.identifier}")
                self.stdout.write(self.style.ERROR(f"Error processing {current_date} for {site.identifier}: {e}"))

            current_date = next_date

        return created_count, updated_count, processed_pageviews
