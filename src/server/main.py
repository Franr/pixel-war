#!/usr/bin/env python3

import asyncio
import importlib.util
import logging

from src.tui import Tui

logger = logging.getLogger()

def check_websockets() -> bool:
    return importlib.util.find_spec("websockets") != None

async def run_server():
    # start the frontend
    app = Tui()
    await app.run_async()

if __name__ == "__main__":
    asyncio.run(run_server())
