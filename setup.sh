#!/bin/bash

echo "🚀 Setting up GEMINIRECON Enterprise Platform..."

# Check for Docker
if ! [ -x "$(command -v docker)" ]; then
  echo "❌ Error: docker is not installed." >&2
  exit 1
fi

# Check for Docker Compose
if ! [ -x "$(command -v docker-compose)" ]; then
  echo "❌ Error: docker-compose is not installed." >&2
  exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "📝 Creating .env file..."
  cp .env.example .env
  echo "⚠️  Please update .env with your API keys!"
fi

# Build and start services
echo "🐳 Building Docker containers..."
docker-compose build

echo "✅ Setup complete! To start the platform, run: docker-compose up -d"
echo "🌐 API will be available at http://localhost:8000"
echo "📊 Dashboard will be available at http://localhost:5173 (if frontend is running)"
