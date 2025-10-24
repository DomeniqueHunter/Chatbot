import asyncio
import base64
import os
import struct
import ssl
from typing import Tuple, Union
from urllib.parse import urlparse

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WebSocketError(Exception):
    pass


class WSState:
    def __init__(self, name:str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return self._name


class WSConnectionInfo:
    def __init__(self, state:WSState):
        self.state = state


class AsyncWebSocketConnection:
    def __init__(self, reader:asyncio.StreamReader, writer:asyncio.StreamWriter, addr:Tuple[str, int]):
        self.reader = reader
        self.writer = writer
        self.addr = addr
        self.state = WSState("CONNECTING")
        self.connection = WSConnectionInfo(self.state)
        self.closed = False

    def _set_state(self, new_state:str) -> None:
        self.state = WSState(new_state)
        self.connection.state = WSState(new_state)

    async def _recv_exact(self, n:int) -> bytes:
        data = b""
        while len(data) < n:
            chunk = await self.reader.read(n - len(data))
            if not chunk:
                self._set_state("CLOSED")
                raise WebSocketError("Connection closed during read")
            data += chunk
        return data

    async def send_frame(self, opcode:int, payload:bytes=b"") -> None:
        if self.state.name in {"CLOSING", "CLOSED"}:
            return
        fin_and_opcode = 0x80 | (opcode & 0x0F)
        mask_bit = 0x80
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

    async def recv_frame(self) -> Tuple[int, bytes]:
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

    async def send_text(self, text:str) -> None:
        await self.send_frame(0x1, text.encode("utf-8"))

    async def send_binary(self, data:bytes) -> None:
        await self.send_frame(0x2, data)

    async def send_ping(self, payload:bytes=b"") -> None:
        await self.send_frame(0x9, payload)

    async def send_pong(self, payload:bytes=b"") -> None:
        await self.send_frame(0xA, payload)

    async def send(self, data:Union[str, bytes]) -> None:
        if isinstance(data, str):
            await self.send_text(data)
        elif isinstance(data, (bytes, bytearray)):
            await self.send_binary(bytes(data))
        else:
            raise TypeError("send() accepts only str or bytes")

    async def recv(self) -> Union[str, bytes]:
        while self.state.name not in {"CLOSING", "CLOSED"}:
            try:
                opcode, payload = await self.recv_frame()
            except WebSocketError:
                self._set_state("CLOSED")
                return b""
            if opcode == 0x1:
                return payload.decode("utf-8", errors="replace")
            if opcode == 0x2:
                return payload
            if opcode == 0x9:
                await self.send_pong(payload)
                continue
            if opcode == 0xA:
                continue
            if opcode == 0x8:
                if self.state.name not in {"CLOSING", "CLOSED"}:
                    await self.close()
                return ""
            await self.close(1002, "protocol error")
            return b""
        return b""

    async def close(self, code:int=1000, reason:str="") -> None:
        if self.state.name in {"CLOSING", "CLOSED"}:
            return
        self._set_state("CLOSING")
        payload = struct.pack("!H", code) + reason.encode("utf-8")
        try:
            await self.send_frame(0x8, payload)
        except Exception:
            pass
        try:
            self.writer.close()
        except Exception:
            pass
        try:
            await self.writer.wait_closed()
        except Exception:
            pass
        self._set_state("CLOSED")
        self.closed = True

    async def __aenter__(self) -> "AsyncWebSocketConnection":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def connect(uri:str) -> AsyncWebSocketConnection:
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
    resp = await reader.readuntil(b"\r\n\r\n")
    if b"101" not in resp.splitlines()[0]:
        raise RuntimeError(f"WebSocket handshake failed:\n{resp.decode(errors='ignore')}")
    ws._set_state("OPEN")
    return ws

