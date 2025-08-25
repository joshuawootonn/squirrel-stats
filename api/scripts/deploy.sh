#!/bin/bash
# Deploy script that handles migrations

set -e

echo "🚀 Starting deployment..."

# Load environment variables
echo "📦 Loading environment variables..."
export $(grep -v '^#' .env.prod | grep -v '^$' | xargs)

# Deploy the application
echo "🔧 Deploying application..."
kamal deploy

# Run migrations
echo "🗄️  Running database migrations..."
kamal app exec 'python manage.py migrate'

echo "✅ Deployment completed successfully!"
echo "🌐 Your API is available at: https://api.usesquirrelstats.com"
