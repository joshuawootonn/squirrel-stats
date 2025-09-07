"""
OpenTelemetry configuration for Django app and queue workers.
"""

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Global flag to prevent multiple configurations
_telemetry_configured = False


def configure_opentelemetry(service_name: str, dataset_name: str):
    """
    Configure OpenTelemetry tracing for the given service.

    Args:
        service_name: Name of the service (e.g., 'server', 'queue-workers')
        dataset_name: Axiom dataset name (e.g., 'server', 'queue-workers')
    """
    global _telemetry_configured

    # Check if already configured to avoid multiple TracerProvider warnings
    if _telemetry_configured:
        return trace.get_tracer(service_name)

    # Define the service name resource
    resource = Resource(attributes={SERVICE_NAME: service_name})

    # Create a TracerProvider with the defined resource
    provider = TracerProvider(resource=resource)

    # Get Axiom configuration from environment variables
    axiom_api_token = os.getenv("AXIOM_API_TOKEN")
    axiom_domain = os.getenv("AXIOM_DOMAIN", "api.axiom.co")

    if not axiom_api_token:
        raise ValueError(
            "AXIOM_API_TOKEN environment variable is required. " "Please set it in your .env.prod file or environment."
        )

    # Configure the OTLP/HTTP Span Exporter with necessary headers and endpoint
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"https://{axiom_domain}/v1/traces",
        headers={
            "Authorization": f"Bearer {axiom_api_token}",
            "X-Axiom-Dataset": dataset_name,
        },
    )

    # Create a BatchSpanProcessor with the OTLP exporter
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)

    # Set the TracerProvider as the global tracer provider
    trace.set_tracer_provider(provider)

    # Mark as configured to prevent duplicate setups
    _telemetry_configured = True

    # Return a tracer for external use
    return trace.get_tracer(service_name)


def configure_telemetry():
    """Configure OpenTelemetry for the application."""
    dataset_name = os.getenv("AXIOM_DATASET", "server")
    return configure_opentelemetry("server", dataset_name)


# Legacy alias for backward compatibility
def configure_server_telemetry():
    """Configure OpenTelemetry for the Django server."""
    return configure_telemetry()


# Global tracers for easy access
server_tracer = None


def get_tracer():
    """Get or create the tracer."""
    global server_tracer
    if server_tracer is None:
        server_tracer = configure_telemetry()
    return server_tracer
