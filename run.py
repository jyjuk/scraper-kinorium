"""
Run script that sets Windows event loop policy before starting uvicorn.
This is required for Playwright to work on Windows with async subprocess.
"""
import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,  # Disable reload for Windows compatibility
        loop="asyncio"  # Use asyncio loop instead of uvloop
    )
