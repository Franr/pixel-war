import asyncio
import secrets
from time import sleep

from shared.commands import Login, Move, Shoot
from shared.protocol import MessageProtocol
from shared.constants import Direction



class GameClientProtocol(MessageProtocol):

    def __init__(self, client_id, correlation_id):
        super().__init__()
        self.client_id = client_id
        self.correlation_id = correlation_id

    def connection_made(self, transport):
        super().connection_made(transport)
        print("[CLIENT] Connected to server.")

    def message_received(self, message: dict):
        if message["action"] == "send_map":
            return

        print(f"[CLIENT] Received update from server: {message}")
        if message["action"] == "create_object" and message["correlation_id"] == self.correlation_id:
            uid = message["obj_data"][0]
            print(f"This is yourself: {uid}")

            # self.send_message(Move(uid=uid, direction=Direction.EAST))
            # if self.client_id == 1:
                # sleep(1)
                # self.send_message(Shoot(uid=uid, direction=Direction.EAST))

    def connection_lost(self, exc):
        print("[CLIENT] Disconnected from server.")


async def run_client_instance(client_id: int, team: int):
    loop = asyncio.get_running_loop()
    correlation_id = secrets.token_hex(8)
    transport, protocol = await loop.create_connection(
        lambda: GameClientProtocol(client_id, correlation_id),
        "127.0.0.1",
        8888
    )

    print(f"Client {client_id} connected. Running... Press Ctrl+C to stop.")

    # first thing after connecting, we need to Login into the game
    protocol.send_message(Login(team=team, correlation_id=correlation_id))

    try:
        # Keep the coroutine running indefinitely
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        # Triggered when main task is cancelled via Ctrl+C
        pass
    finally:
        print(f"Closing client {client_id} connection...")
        transport.close()


# async def main():
    # await asyncio.gather(
        # run_client_instance(1, 0),
        # run_client_instance(2, 1)
    # )

if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(run_client_instance(1, 0))
