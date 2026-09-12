#!/usr/bin/env python3

import asyncio
import logging

from src.game import ServerHandler

logger = logging.getLogger()


async def run_server():
    sh = ServerHandler()
    await sh.run()

if __name__ == "__main__":
    asyncio.run(run_server())
