# GitHub Codespaces Setup Guide

## 🚀 Quick Start (1 Click)

### Launch Codespace
1. Go to your repo: https://github.com/saiarjunkoyalkar756-sudo/GEMINIRECON-
2. Click **Code** → **Codespaces** → **Create codespace on main**
3. Wait for container to build (~3-5 minutes)
4. Automatic setup runs, environment ready! ✅

## 📋 What's Pre-Configured

### Languages & Runtimes
- ✅ **Node.js 20** - Frontend (React, TypeScript, Vite)
- ✅ **Python 3.11** - Backend (FastAPI)
- ✅ **PostgreSQL 15** - Database (pgvector enabled)
- ✅ **Redis** - Task queue & caching

### VS Code Extensions
- ✅ Python (linting, debugging)
- ✅ ESLint + Prettier (code formatting)
- ✅ Docker support
- ✅ GitHub Copilot
- ✅ GitLens
- ✅ Thunder Client (API testing)
- ✅ YAML support

### Port Forwarding (Auto-Configured)
- `3000` - Next.js (if used)
- `5173` - Vite Frontend
- `8000` - FastAPI Backend
- `5432` - PostgreSQL
- `6379` - Redis

## 🔧 First Time Setup

After Codespace launches, the `postCreateCommand.sh` automatically:

1. ✅ Installs all dependencies
2. ✅ Builds frontend
3. ✅ Creates `.env.local` template
4. ✅ Starts PostgreSQL and Redis
5. ✅ Displays next steps

## 🏃 Running the Application

### In Terminal 1 - Backend
```bash
cd backend
python main.py
# Runs on http://localhost:8000
```

### In Terminal 2 - Frontend
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### Access URLs
- **Frontend**: https://yourcodespace-xxxxx.github.dev:5173
- **Backend API**: https://yourcodespace-xxxxx.github.dev:8000
- **API Docs**: https://yourcodespace-xxxxx.github.dev:8000/docs

## ��� Environment Variables

The `.env.local` is created automatically. Update with your keys:

```bash
# Edit in Codespace
cat .env.local

# Add your keys:
GEMINI_API_KEY=your_actual_key
OPENROUTER_API_KEY=your_actual_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
UPSTASH_REDIS_URL=your_redis_url
```

## 💾 Persisting Codespace

### Your files are automatically saved:
- ✅ Changes to files
- ✅ VS Code settings
- ✅ Extensions
- ✅ Terminal history

### Restore after closing:
1. Open Codespace again → Same state restored
2. All dependencies cached → Faster startup

## 🛠️ Common Commands

```bash
# Reinstall dependencies
npm install && pip install -r requirements.txt

# Run tests
npm run test        # Frontend
pytest backend/     # Backend

# Format code
npm run lint
black backend/

# Stop services
Ctrl+C in each terminal

# View logs
# Terminal → Run Task → Show Backend Logs
```

## 🧹 Clean Up

```bash
# Remove Codespace
Code → Codespaces → Delete Codespace
# OR via GitHub → Codespaces tab

# Keep running (always-on)
Right-click Codespace → Change retention → Set to 30 days
```

## 📊 Codespace Hardware Specs

| Resource | Free Tier | Pro Tier |
|----------|-----------|----------|
| vCPU | 2 | 4 |
| RAM | 4GB | 8GB |
| Storage | 32GB | 64GB |
| Hours/Month | 60 | 180 |

**Your setup uses:** 2 vCPU, 4GB RAM, 32GB storage

## 🔗 Advanced: Sync with Local Git

```bash
# Pull latest changes
git pull origin main

# Push your changes
git add .
git commit -m "feat: your change"
git push origin main

# Create PR from Codespace
gh pr create --title "Your PR" --body "Description"
```

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Database connection error
```bash
# Restart PostgreSQL
service postgresql restart

# Check status
pg_isready
```

### Node modules corrupted
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Redis connection failed
```bash
# Restart Redis
redis-server --daemonize yes

# Test connection
redis-cli ping
# Should return: PONG
```

## 📚 Documentation

- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
- [devcontainer.json Reference](https://containers.dev/implementors/json_reference/)
- [VS Code in Codespaces](https://code.visualstudio.com/docs/remote/codespaces)

## 🎯 Tips & Tricks

1. **Share Codespace**: Codespaces → Share (live collaboration)
2. **Offline use**: Create Codespace, then work offline
3. **GitHub Copilot**: Pre-enabled, use Ctrl+Space for suggestions
4. **Terminal multiplexing**: Use tmux or just open multiple terminals
5. **SSH into Codespace**: `ssh-keyscan` already configured

---

**Ready to code? Click "Create codespace on main" to start! 🚀**
