import asyncio
import base64
import hashlib
import os
import struct
import ssl
from typing import Tuple, Optional, Union
from urllib.parse import urlparse

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WebSocketError(Exception):
    """Generic WebSocket error."""


class AsyncWebSocketConnection:
    """Represents one async WebSocket connection."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, addr: Tuple[str, int]):
        self.reader = reader
        self.writer = writer
        self.addr = addr
        self.closed = False
        
    def state(self):
        return "OPEN" # TODO better state

    async def close(self, code: int=1000, reason: str="") -> None:
        """Send close frame and close connection."""
        if self.closed:
            return
        payload = struct.pack("!H", code) + reason.encode("utf-8")
        try:
            await self.send_frame(0x8, payload)
        except Exception:
            pass
        self.writer.close()
        try:
            await self.writer.wait_closed()
        except Exception:
            pass
        self.closed = True

    async def send_frame(self, opcode: int, payload: bytes = b"") -> None:
        """Send a WebSocket frame. Clients must mask frames."""
        if self.closed:
            return
    
        fin_and_opcode = 0x80 | (opcode & 0x0F)
        mask_bit = 0x80  # set masking bit
        length = len(payload)
    
        if length < 126:
            header = struct.pack("!BB", fin_and_opcode, mask_bit | length)
        elif length < (1 << 16):
            header = struct.pack("!BBH", fin_and_opcode, mask_bit | 126, length)
        else:
            header = struct.pack("!BBQ", fin_and_opcode, mask_bit | 127, length)
    
        masking_key = os.urandom(4)
        masked_payload = bytes(payload[i] ^ masking_key[i % 4] for i in range(length))
    
        self.writer.write(header + masking_key + masked_payload)
        await self.writer.drain()


    async def send_text(self, text: str) -> None:
        """Send a text frame."""
        await self.send_frame(0x1, text.encode("utf-8"))

    async def send_binary(self, data: bytes) -> None:
        """Send a binary frame."""
        await self.send_frame(0x2, data)

    async def send_ping(self, payload: bytes=b"") -> None:
        """Send ping frame."""
        await self.send_frame(0x9, payload)

    async def send_pong(self, payload: bytes=b"") -> None:
        """Send pong frame."""
        await self.send_frame(0xA, payload)

    async def _recv_exact(self, n: int) -> bytes:
        """Read exactly n bytes."""
        data = b""
        while len(data) < n:
            chunk = await self.reader.read(n - len(data))
            if not chunk:
                raise WebSocketError("Connection closed during read")
            data += chunk
        return data

    async def recv_frame(self) -> Tuple[int, bytes]:
        """Receive one WebSocket frame and return (opcode, payload)."""
        header = await self._recv_exact(2)
        b1, b2 = header[0], header[1]
        opcode = b1 & 0x0F
        masked = (b2 >> 7) & 1
        payload_len = b2 & 0x7F

        if payload_len == 126:
            ext = await self._recv_exact(2)
            (payload_len,) = struct.unpack("!H", ext)
        elif payload_len == 127:
            ext = await self._recv_exact(8)
            (payload_len,) = struct.unpack("!Q", ext)

        masking_key = b""
        if masked:
            masking_key = await self._recv_exact(4)

        payload = b""
        if payload_len:
            payload = await self._recv_exact(payload_len)

        if masked:
            payload = bytes(payload[i] ^ masking_key[i % 4] for i in range(len(payload)))

        return opcode, payload

    async def send(self, data: Union[str, bytes]) -> None:
        """Send text or binary; default str -> text, bytes -> binary."""
        if isinstance(data, str):
            await self.send_text(data)
        elif isinstance(data, (bytes, bytearray)):
            await self.send_binary(bytes(data))
        else:
            raise TypeError("send() accepts only str or bytes")

    async def recv(self) -> Union[str, bytes]:
        """Receive next text or binary message; returns str for text, bytes for binary."""
        while not self.closed:
            opcode, payload = await self.recv_frame()
            if opcode == 0x1:
                return payload.decode("utf-8", errors="replace")
            elif opcode == 0x2:
                return payload
            elif opcode == 0x9:  # ping
                await self.send_pong(payload)
            elif opcode == 0xA:  # pong
                continue
            elif opcode == 0x8:  # close
                await self.close()
                return ""
            else:
                await self.close(1002, "protocol error")
                return ""

    async def __aenter__(self) -> "AsyncWebSocketConnection":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def connect(uri: str) -> AsyncWebSocketConnection:
    """
    Connect to a WebSocket URI, perform handshake, and return AsyncWebSocketConnection.
    
    Example:
        ws = await connect("ws://127.0.0.1:8765/chat")
    """
    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()
    host = parsed.hostname
    path = parsed.path or "/"
    port = parsed.port

    if scheme == "ws":
        use_ssl = False
        port = port or 80
    elif scheme == "wss":
        use_ssl = True
        port = port or 443
    else:
        raise ValueError(f"Unsupported URI scheme: {scheme}")

    ssl_context = ssl.create_default_context() if use_ssl else None
    reader, writer = await asyncio.open_connection(host, port, ssl=ssl_context)
    ws = AsyncWebSocketConnection(reader, writer, (host, port))

    # generate random key for handshake
    key = base64.b64encode(os.urandom(16)).decode("utf-8")
    query = f"?{parsed.query}" if parsed.query else ""
    request = (
        f"GET {path}{query} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        f"Origin: http://{host}\r\n"
        "\r\n"
    )
    writer.write(request.encode("utf-8"))
    await writer.drain()

    # read handshake response
    resp = await reader.readuntil(b"\r\n\r\n")
    if b"101" not in resp.splitlines()[0]:
        raise RuntimeError(f"WebSocket handshake failed:\n{resp.decode(errors='ignore')}")
    return ws


# Example usage
async def main() -> None:
    async with await connect("127.0.0.1", 8765) as ws:
        await ws.send("Hello world")
        msg = await ws.recv()
        print("Received:", msg)


if __name__ == "__main__":
    asyncio.run(main())
