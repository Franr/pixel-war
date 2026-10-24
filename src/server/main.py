#!/usr/bin/env python3

import asyncio
import importlib.util
import logging

from src.server import TcpServerHandler
from src.webserver import WebSocketServerHandler  # TODO: check if break if no dependency installed
from src.tui import Tui

logger = logging.getLogger()

def check_websockets() -> bool:
    return importlib.util.find_spec("websockets") != None

async def run_server():
    if check_websockets():
        sh = WebSocketServerHandler()
        # server = await serve(echo, "localhost", 8765)
        # await server.serve_forever()
    else:
        # start the server
        sh = TcpServerHandler()
    task = asyncio.create_task(sh.run())
    # await task  # required if there is no TUI

    # start the frontend
    app = Tui(sh)
    # run Textual within the EXISTING event loop
    await app.run_async()

if __name__ == "__main__":
    asyncio.run(run_server())
