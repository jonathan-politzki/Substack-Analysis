#!/bin/bash

# Substack Analyzer - Docker Runner
echo "🚀 Starting Substack Analyzer..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists and source it
if [ -f .env ]; then
    echo "📄 Found .env file, loading environment variables..."
    export $(grep -v '^#' .env | xargs)
fi

# Build and run with docker-compose
echo "🔨 Building and starting the container..."
docker-compose up --build -d

echo "✅ Substack Analyzer is now running!"
echo "🌐 Open your browser and go to: http://localhost:8501"
echo ""
echo "To stop the container, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f" 