#!/bin/bash

# Activate virtual environment and set up local development
echo "🚀 Activating development environment..."

# Activate virtual environment
source ../squirrel-stats/bin/activate

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres@localhost:5438/squirrel_stats"
export DEBUG=1
export FRONTEND_URL="http://localhost:7777"
export REDIS_URL="redis://localhost:6379/0"
export MAILPACE_API_KEY=""
export DEFAULT_FROM_EMAIL="noreply@localhost"

echo "✅ Virtual environment activated"
echo "✅ Environment variables set"
echo ""
echo "📋 Next steps:"
echo "1. Start services: docker-compose up -d postgres redis"
echo "2. Run Django: python manage.py runserver"
echo ""
echo "💡 To use this setup, run: source activate_dev.sh"
