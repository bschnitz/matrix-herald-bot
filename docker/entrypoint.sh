#!/bin/bash
set -e

echo "🔧 Installing/updating Poetry dependencies..."

cd /app
poetry install --only main --no-root

cd /matrix-guard-api
poetry install --only main --no-root

echo "✅ Dependencies installed successfully"
echo "🚀 Starting Supervisor..."

exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
