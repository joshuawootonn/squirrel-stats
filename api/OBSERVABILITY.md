# OpenTelemetry Observability Setup for Squirrel Stats

This document describes the OpenTelemetry observability setup for the Squirrel Stats Django application and queue workers, sending traces to Axiom.

## Overview

The setup includes:

- **Django Server Tracing**: HTTP requests, database queries, custom spans
- **Queue Worker Tracing**: RQ job processing, Redis operations, management commands
- **Custom Instrumentation**: Pageview tracking with detailed attributes
- **Axiom Integration**: Separate datasets for server and queue worker traces

## Configuration

### Dataset

- **Single Dataset**: `server` - Contains all traces (Django HTTP requests, API calls, background jobs, schedulers)

### Service Names

- **Server Service**: `server`

### Axiom Configuration

- **Domain**: `api.axiom.co` (US region) - configurable via `AXIOM_DOMAIN`
- **API Token**: Configured via `AXIOM_API_TOKEN` environment variable
- **Dataset**: Configurable via `AXIOM_DATASET` (defaults to `server`)

## Installation

1. **Set up Environment Variables**:

   ```bash
   cd api/
   cp axiom.env.example .env.prod
   # Edit .env.prod with your actual Axiom API token
   export $(xargs < .env.prod)
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Test Installation**:
   ```bash
   python install_otel.py
   ```

## File Changes

### New Files

- `otel_config.py` - OpenTelemetry configuration for both server and workers
- `install_otel.py` - Installation and testing script
- `axiom.env.example` - Example environment variables file for Axiom configuration
- `OBSERVABILITY.md` - This documentation

### Modified Files

- `requirements.txt` - Added OpenTelemetry dependencies
- `manage.py` - Added Django instrumentation initialization
- `api/settings.py` - Added server telemetry configuration
- `server/management/commands/rq_worker.py` - Added worker telemetry and Redis instrumentation
- `server/management/commands/queue_current_hour.py` - Added custom tracing spans
- `server/management/commands/aggregate_hourly_stats.py` - Added comprehensive tracing
- `server/views/pageviews.py` - Added custom spans for pageview tracking

## Trace Data

### Server Traces (`server` dataset)

- HTTP requests to Django endpoints
- Database queries (automatic via Django instrumentation)
- Custom pageview tracking spans with attributes:
  - `pageview.site_identifier`
  - `pageview.hostname`
  - `pageview.path`
  - `pageview.method`
  - `pageview.device_type`
  - `pageview.browser`
  - `pageview.os`
  - `pageview.created`
  - `pageview.error` (if any)


### Trace Attributes

All traces include standard OpenTelemetry attributes plus custom attributes specific to the application:

#### Command Attributes

- `command.hours_to_process`
- `command.site_identifier`
- `command.sites_count`
- `command.total_created`
- `command.total_updated`
- `command.total_processed`

#### Aggregation Attributes

- `site.identifier`
- `aggregation.start`
- `aggregation.end`
- `execution.mode` (enqueued/direct)

## Usage

## Environment Variables

The following environment variables configure the Axiom integration:

| Variable          | Description            | Default        | Required |
| ----------------- | ---------------------- | -------------- | -------- |
| `AXIOM_API_TOKEN` | Your Axiom API token   | None           | Yes      |
| `AXIOM_DOMAIN`    | Axiom API domain       | `api.axiom.co` | No       |
| `AXIOM_DATASET`   | Dataset for all traces | `server`       | No       |

### Loading Environment Variables

Based on your memory preference, load environment variables using:

```bash
export $(xargs < .env.prod)
```

### Starting Services with Observability

**All-in-One Workers Service**:

```bash
docker-compose up
```

- Single `workers` service runs everything:
  - 1 RQ worker (processes jobs)
  - 4 schedulers (queues jobs at different intervals)
- All traces appear in the unified `server` dataset
- Includes HTTP requests, job processing, Redis operations, and management commands

### Viewing Traces in Axiom

Navigate to the `server` dataset in your Axiom dashboard to see all traces:

- HTTP requests and API calls
- Background job processing
- Queue scheduling operations
- Database queries and Redis operations

### Useful Queries

#### Find slow pageview requests:

```
_dataset == "server"
| where name == "track_pageview"
| where duration > 1000000  // 1 second in microseconds
```

#### Monitor queue job processing:

```
_dataset == "queue-workers"
| where name == "aggregate_hourly_stats_command"
| summarize count() by bin(_time, 1h)
```

#### Track pageview errors:

```
_dataset == "server"
| where name == "track_pageview"
| where attributes.custom["pageview.error"] != ""
```

## Troubleshooting

### Common Issues

1. **"python: can't open file '/app/manage.py'" Error**:

   - **Cause**: Running docker-compose from wrong directory
   - **Fix**: Always run from the root directory: `cd api && docker-compose up`
   - **Not**: `docker-compose -f api/docker-compose.yml up` from sub directory

2. **Import Errors**: Ensure all OpenTelemetry packages are installed

   ```bash
   pip install -r requirements.txt
   ```

3. **No Traces in Axiom**: Check that:

   - API token is correct in environment variables
   - Dataset names match your Axiom configuration
   - Network connectivity to `api.axiom.co`

4. **Linting Errors**: The OpenTelemetry imports may show as unresolved until packages are installed

### Testing Traces

1. **Test Server Traces**:

   ```bash
   curl "http://localhost:8000/api/v1/track?sid=test&h=localhost&p=/test"
   ```

2. **Test Worker Traces**:
   ```bash
   python manage.py queue_current_hour
   ```

## Security Considerations

- API token is now configured via environment variables
- Keep your `.env.prod` file secure and never commit it to version control
- The `axiom.env.example` file should be committed as a template
- Consider using a secrets management system for production deployments

## Performance Impact

OpenTelemetry instrumentation has minimal performance impact:

- Automatic instrumentation adds ~1-5ms per request
- Custom spans add ~0.1-1ms per span
- Batching reduces network overhead
- Consider sampling for high-traffic applications

## Extending Observability

### Adding Custom Spans

```python
from otel_config import get_tracer

def my_function():
    tracer = get_tracer()
    with tracer.start_as_current_span("my_custom_operation") as span:
        span.set_attribute("custom.attribute", "value")
        # Your code here
```

### Adding More Instrumentation

Additional instrumentation libraries can be added to `requirements.txt`:

- `opentelemetry-instrumentation-psycopg2` - PostgreSQL queries
- `opentelemetry-instrumentation-requests` - HTTP client requests
- `opentelemetry-instrumentation-logging` - Log correlation

## References

- [Axiom OpenTelemetry Django Guide](https://axiom.co/docs/guides/opentelemetry-django)
- [OpenTelemetry Python Documentation](https://opentelemetry-python.readthedocs.io/)
- [OpenTelemetry Instrumentation Registry](https://opentelemetry.io/registry/?language=python)
