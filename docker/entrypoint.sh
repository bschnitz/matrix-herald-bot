#!/bin/bash
set -e

echo "🔧 Installing/updating Poetry dependencies..."
cd /app
poetry install --only main --no-root

echo "✅ Dependencies installed successfully"
echo "🚀 Starting Matrix Herald Bot..."
exec poetry run python -m matrix_herald_bot.main
