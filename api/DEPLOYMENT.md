# Squirrel Stats Deployment

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Server    │    │     Redis       │    │   Workers       │
│                 │    │                 │    │                 │
│ • Django API    │    │ • RQ Queue      │    │ • RQ Worker     │
│ • Gunicorn      │    │ • Job Storage   │    │ • Schedulers    │
│ • Port 8000     │    │ • Port 6379     │    │ • Aggregation   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components

- **Web**: Django API server (Gunicorn)
- **Workers**: Background job processing (RQ + Redis)
- **Redis**: Message queue and job storage
- **Database**: SQLite with hourly aggregated stats

### Worker Processes

- **RQ Worker**: Processes aggregation jobs from Redis queue
- **Current Hour Scheduler**: Queues aggregation for current hour (every minute)
- **Backfill Scheduler**: Queues missing hours from last 7 days (every hour)

## Deployment Commands

### Environment Setup

```bash
# Load production environment
export $(xargs < .env.prod)
# Load local environment
export $(xargs < .env.local)
```

### Full Deployment

```bash
# Deploy everything
kamal deploy

# Deploy specific role
kamal deploy --roles web
kamal deploy --roles workers
```

### Container Management

```bash
# Restart workers
kamal app boot --roles workers

# Check logs
kamal app logs

# Execute commands
kamal app exec "python manage.py migrate"
kamal app exec --role workers "python manage.py shell"
```

### Database Migrations

```bash
# Run migrations
kamal app exec "python manage.py migrate"

# Create migration
python manage.py makemigrations
git add server/migrations/
git commit -m "Add migration"
kamal deploy
```

## Management Commands

### Aggregation

```bash
# Queue current hour for all sites
python manage.py queue_current_hour

# Queue backfill for missing hours
python manage.py queue_backfill_missing_hours

# Manual aggregation for specific site/time
python manage.py aggregate_hourly_stats \
  --site site-id \
  --start "2025-08-29T12:00:00+00:00" \
  --end "2025-08-29T13:00:00+00:00"
```

### Worker Management

```bash
# Start RQ worker
python manage.py rq_worker --queue aggregations

# Check Redis connection
python manage.py shell
>>> import redis
>>> r = redis.from_url('redis://localhost:6379/0')
>>> r.ping()
```

## Troubleshooting

### Workers Not Starting

```bash
# Check health status
kamal app exec --role workers "ps aux"

# Check Redis connection
kamal app exec --role workers "python -c 'import redis; print(redis.from_url(\"redis://5.161.248.77:6379/0\").ping())'"

# Restart workers
kamal app boot --roles workers
```

### Database Issues

```bash
# Check migrations
kamal app exec "python manage.py showmigrations"

# Apply migrations
kamal app exec "python manage.py migrate"

```

### Redis Issues

```bash
# Check Redis accessory
kamal accessory logs redis

# Restart Redis
kamal accessory reboot redis

# Check Redis data
kamal accessory exec redis redis-cli ping
```

## Monitoring

### Check Job Status

```bash
# View recent logs
kamal app logs | tail -50

# Check specific worker logs
kamal app logs | grep "aggregations:"

# Monitor job completion
kamal app logs | grep "Job OK"
```