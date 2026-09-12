import asyncio
import json
import struct
from dataclasses import asdict

from .commands import Command


class MessageProtocol(asyncio.Protocol):
    """
    Base protocol that handles TCP stream framing using a 4-byte length prefix.
    Payloads are serialized/deserialized as standard JSON objects.
    """
    HEADER_SIZE = 4

    def __init__(self):
        self.transport: asyncio.Transport
        self._buffer = bytearray()
        self._payload_size = None

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport

    def data_received(self, data):
        self._buffer.extend(data)
        
        while True:
            # Read header to determine payload size
            if self._payload_size is None:
                if len(self._buffer) < self.HEADER_SIZE:
                    break  # Wait for full header
                self._payload_size = struct.unpack(">I", self._buffer[:self.HEADER_SIZE])[0]
                del self._buffer[:self.HEADER_SIZE]

            # Read payload data based on expected size
            if len(self._buffer) < self._payload_size:
                break  # Wait for complete payload
            
            payload_data = self._buffer[:self._payload_size]
            del self._buffer[:self._payload_size]
            self._payload_size = None

            # Process payload
            try:
                message = json.loads(payload_data.decode("utf-8"))
                self.message_received(message)
            except (UnicodeError, json.JSONDecodeError) as e:
                print(f"Error parsing message: {e}")

    def send_message(self, data: Command):
        """Encodes and frames a dictionary payload for sending."""
        payload = json.dumps(asdict(data)).encode("utf-8")
        header = struct.pack(">I", len(payload))
        self.transport.write(header + payload)

    def message_received(self, message: dict):
        """Override this method to handle incoming parsed messages."""
