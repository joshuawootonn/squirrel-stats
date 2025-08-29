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

# Wait for all background processes
wait
