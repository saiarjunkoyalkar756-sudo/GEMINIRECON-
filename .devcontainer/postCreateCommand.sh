#!/bin/bash
set -e

echo "🚀 Setting up GEMINIRECON development environment..."

# Update packages
echo "📦 Installing system packages..."
apt-get update && apt-get install -y \
  build-essential \
  curl \
  git \
  postgresql-client \
  redis-tools \
  wget \
  2>&1 | grep -v "^Get:\|^Hit:\|^Reading\|^Building" || true

# Setup Python environment
echo "🐍 Setting up Python..."
python3 -m pip install --upgrade pip setuptools wheel 2>&1 | tail -3
cd /workspaces/GEMINIRECON- 2>/dev/null || cd $(pwd)

# Install backend dependencies
if [ -f "backend/requirements.txt" ]; then
  echo "📥 Installing Python dependencies..."
  pip install -r backend/requirements.txt 2>&1 | tail -5
fi

# Install frontend dependencies
if [ -f "frontend/package.json" ]; then
  echo "📥 Installing Node dependencies..."
  cd frontend
  npm install 2>&1 | tail -5
  cd ..
fi

# Create environment file
if [ ! -f ".env.local" ]; then
  echo "📝 Creating .env.local template..."
  cat > .env.local << 'EOF'
# Frontend
VITE_API_URL=http://localhost:8000

# Gemini & API
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Supabase
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Redis
UPSTASH_REDIS_URL=redis://localhost:6379

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/geminirecon

# Environment
NODE_ENV=development
LOG_LEVEL=debug
EOF
  echo "✅ .env.local created - add your API keys!"
fi

# Initialize PostgreSQL
echo "🗄️  Initializing PostgreSQL..."
service postgresql start 2>/dev/null || true
sleep 2
createdb geminirecon 2>/dev/null || echo "Database already exists"

# Start Redis
echo "⚡ Starting Redis..."
service redis-server start 2>/dev/null || redis-server --daemonize yes || true

# Install Python dev tools
echo "🛠️  Installing development tools..."
pip install black pylint pytest pytest-asyncio 2>&1 | tail -3

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Update .env.local with your API keys"
echo "  2. Terminal 1: cd backend && python main.py"
echo "  3. Terminal 2: cd frontend && npm run dev"
echo ""
echo "🌐 Access URLs:"
echo "  • Frontend: http://localhost:5173"
echo "  • Backend: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
