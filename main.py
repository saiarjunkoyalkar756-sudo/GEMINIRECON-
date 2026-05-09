import sys
import asyncio
from dashboard.tui import ReconApp
from core.storage.database import init_db

async def run_app():
    # Initialize database
    await init_db()
    
    # Run TUI
    app = ReconApp()
    await app.run_async()

if __name__ == "__main__":
    if "--cli" in sys.argv:
        # Fallback for simple CLI if needed
        print("CLI mode not implemented yet. Use TUI.")
    else:
        asyncio.run(run_app())
