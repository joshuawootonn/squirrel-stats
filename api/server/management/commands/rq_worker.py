"""
Django management command to run RQ worker.
"""

import os
import sys

from django.core.management.base import BaseCommand

from otel_config import get_tracer

# OpenTelemetry will be initialized by Django settings
# Redis instrumentation should be done once globally

try:
    import redis
    from rq import Queue, Worker
    from rq.job import Job
except ImportError:
    redis = None
    Worker = None
    Queue = None
    Job = None


class Command(BaseCommand):
    help = "Run RQ worker for processing background jobs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--queue",
            type=str,
            default="aggregations",
            help="Queue name to process (default: aggregations)",
        )
        parser.add_argument(
            "--redis-url",
            type=str,
            help="Redis URL (default: from REDIS_URL env var)",
        )

    def handle(self, *args, **options):
        if not redis or not Worker:
            self.stdout.write(self.style.ERROR("RQ and Redis are required. Install with: pip install rq redis"))
            sys.exit(1)

        queue_name = options["queue"]
        redis_url = options.get("redis_url") or os.getenv("REDIS_URL")

        if not redis_url:
            self.stdout.write(
                self.style.ERROR("Redis URL is required. Set REDIS_URL environment variable or use --redis-url")
            )
            sys.exit(1)

        try:
            redis_conn = redis.from_url(redis_url)
            queue = Queue(queue_name, connection=redis_conn)
            worker = Worker([queue], connection=redis_conn)
            tracer = get_tracer()
            with tracer.start_as_current_span("rq_worker") as span:
                span.set_attribute("queue", queue_name)
                span.set_attribute("redis_url", redis_url)

            self.stdout.write(self.style.SUCCESS(f"Starting RQ worker for queue '{queue_name}' on {redis_url}"))

            worker.work()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error starting worker: {e}"))
            sys.exit(1)
