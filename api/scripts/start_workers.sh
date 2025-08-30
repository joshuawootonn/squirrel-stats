#!/bin/bash
# Start RQ workers and schedulers for production

# Start RQ worker in background
python manage.py rq_worker --queue aggregations &

# Start current hour scheduler (every minute)
while true; do
    python manage.py queue_current_hour
    sleep 60
done &

# Start backfill scheduler (every hour)
while true; do
    python manage.py queue_backfill_missing_hours
    sleep 3600
done &

# Start current day scheduler (every hour - to catch new data throughout the day)
while true; do
    python manage.py queue_current_day
    sleep 300
done &

# Start daily backfill scheduler (every 6 hours - to catch any missing days)
while true; do
    python manage.py queue_backfill_missing_days --days=7
    sleep 21600
done &

# Wait for all background processes
wait
