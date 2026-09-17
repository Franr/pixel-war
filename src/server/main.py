#!/usr/bin/env python3

import asyncio
import logging

from src.server import ServerHandler
from src.tui import Tui

logger = logging.getLogger()


async def run_server():
    # start the server
    sh = ServerHandler()
    asyncio.create_task(sh.run())
    # start the frontend
    app = Tui(sh.gh)
    # run Textual within the EXISTING event loop
    await app.run_async()

if __name__ == "__main__":
    asyncio.run(run_server())
