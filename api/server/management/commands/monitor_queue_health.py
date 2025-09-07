"""
Monitor Redis queue health and send metrics to Axiom.

This command checks the current state of all queues and sends detailed
metrics to Axiom for monitoring and alerting purposes.

Run this periodically (every 30-60 seconds) to maintain real-time queue visibility.
"""

import os

from django.core.management.base import BaseCommand

from otel_config import get_tracer

try:
    import redis  # type: ignore
    from rq import Queue, Worker  # type: ignore
    from rq.registry import DeferredJobRegistry, FailedJobRegistry, StartedJobRegistry  # type: ignore

    REDIS_URL = os.getenv("REDIS_URL")
    redis_conn = redis.from_url(REDIS_URL) if REDIS_URL else None
except Exception:  # pragma: no cover
    redis_conn = None
    Queue = None
    Worker = None


class Command(BaseCommand):
    help = "Monitor Redis queue health and send metrics to Axiom"

    def add_arguments(self, parser):
        parser.add_argument(
            "--queue",
            type=str,
            default="aggregations",
            help="Queue name to monitor (default: aggregations)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )

    def handle(self, *args, **options):
        queue_name = options["queue"]
        verbose = options["verbose"]

        tracer = get_tracer()
        with tracer.start_as_current_span("queue_health_check") as span:
            span.set_attribute("queue.name", queue_name)
            span.set_attribute("monitor.type", "health_check")

            if not redis_conn or not Queue:
                span.set_attribute("queue.error", "redis_unavailable")
                span.set_attribute("queue.status", "error")
                self.stdout.write(self.style.ERROR("❌ Redis connection not available"))
                return

            try:
                # Get queue instance
                q = Queue(queue_name, connection=redis_conn)

                # Basic queue metrics
                queue_length = len(q)
                span.set_attribute("queue.length", queue_length)

                # Job registries for detailed metrics
                failed_registry = FailedJobRegistry(queue=q)
                started_registry = StartedJobRegistry(queue=q)
                deferred_registry = DeferredJobRegistry(queue=q)

                failed_count = len(failed_registry)
                started_count = len(started_registry)
                deferred_count = len(deferred_registry)

                span.set_attribute("queue.failed_jobs", failed_count)
                span.set_attribute("queue.started_jobs", started_count)
                span.set_attribute("queue.deferred_jobs", deferred_count)
                span.set_attribute("queue.total_jobs", queue_length + started_count + deferred_count)

                # Worker metrics
                workers = Worker.all(connection=redis_conn)
                active_workers = [w for w in workers if w.state == "busy"]
                idle_workers = [w for w in workers if w.state == "idle"]

                span.set_attribute("workers.total", len(workers))
                span.set_attribute("workers.active", len(active_workers))
                span.set_attribute("workers.idle", len(idle_workers))

                # Health status determination
                if queue_length > 100:
                    status = "overloaded"
                    span.set_attribute("alert.type", "queue_overloaded")
                    span.set_attribute("alert.severity", "high")
                    span.set_attribute("queue.alert", "overloaded")
                    span.set_attribute("queue.alert_threshold", 100)
                elif queue_length > 50:
                    status = "warning"
                    span.set_attribute("queue.warning", "high_queue_length")
                    span.set_attribute("queue.warning_threshold", 50)
                elif failed_count > 10:
                    status = "degraded"
                    span.set_attribute("queue.warning", "high_failure_rate")
                elif len(workers) == 0:
                    status = "no_workers"
                    span.set_attribute("alert.type", "no_workers")
                    span.set_attribute("alert.severity", "critical")
                else:
                    status = "healthy"

                span.set_attribute("queue.status", status)

                # Output based on status
                if status == "overloaded":
                    self.stdout.write(
                        self.style.ERROR(f"🚨 QUEUE OVERLOADED: {queue_length} jobs pending " f"(threshold: 100)")
                    )
                elif status == "warning":
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Queue getting full: {queue_length} jobs pending " f"(threshold: 50)")
                    )
                elif status == "no_workers":
                    self.stdout.write(self.style.ERROR(f"🚨 NO WORKERS AVAILABLE: {queue_length} jobs waiting"))
                elif status == "degraded":
                    self.stdout.write(self.style.WARNING(f"⚠️  High failure rate: {failed_count} failed jobs"))
                else:
                    if verbose:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ Queue healthy: {queue_length} pending, "
                                f"{len(active_workers)}/{len(workers)} workers active"
                            )
                        )

                # Detailed output if verbose
                if verbose:
                    self.stdout.write(f"📊 Queue Metrics for '{queue_name}':")
                    self.stdout.write(f"   • Pending jobs: {queue_length}")
                    self.stdout.write(f"   • Started jobs: {started_count}")
                    self.stdout.write(f"   • Failed jobs: {failed_count}")
                    self.stdout.write(f"   • Deferred jobs: {deferred_count}")
                    self.stdout.write(f"   • Total workers: {len(workers)}")
                    self.stdout.write(f"   • Active workers: {len(active_workers)}")
                    self.stdout.write(f"   • Status: {status}")

            except Exception as e:
                span.set_attribute("queue.error", str(e))
                span.set_attribute("queue.status", "error")
                span.set_attribute("alert.type", "monitoring_error")
                span.set_attribute("alert.severity", "medium")

                self.stdout.write(self.style.ERROR(f"❌ Failed to monitor queue '{queue_name}': {e}"))
