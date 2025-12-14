from framework.api import get_ticket
from framework.lib.config import Config
from framework import opcode
import json
import websockets.client
import asyncio
from collections import deque
from typing import Deque, Optional, Tuple


def _parsed(op:str, msg:str | None="") -> tuple[str,str]: 
    return op, msg


class Communication:

    def __init__(self, bot) -> None:
        self.bot = bot
        self.config: Config = self.bot.config
        self.connection = None

        self._send_queue: Deque[Tuple[str, dict | None]] = deque()
        self._queue_condition = asyncio.Condition()
        self._sender_task: Optional[asyncio.Task] = None
        
        self._recv_queue: Deque[str] = deque()
        self._recv_condition = asyncio.Condition()
        self._receiver_task: Optional[asyncio.Task] = None

    async def identify(self) -> None:
        data = {
            "method": "ticket",
            "ticket": await self.get_api_ticket(),
            "account": str(self.config.account),
            "character": str(self.config.character),
            "cname": "Python Client",
            "cversion": self.bot.version,
        }

        await self.message(opcode.IDENTIFY, data)
        await self.read()

    async def connect(self) -> None:
        uri = self.config.protocol + self.config.server + self.config.endpoint

        try:
            self.connection = await websockets.client.connect(uri)
            print(f"connected to: {uri} - {self.status()}")

        except Exception as e:
            print(f"could not connect to: {uri}")
            print(f"error: {e}")
            self.connection = None

    async def start_sender(self) -> None:
        if self._sender_task is None:
            self._sender_task = asyncio.create_task(self._send_loop())
    
    async def start_receiver(self) -> None:
        if self._receiver_task is None:
            self._receiver_task = asyncio.create_task(self._recv_loop())
           
    async def start(self) -> None:
        # await self.start_receiver()
        await self.start_sender()

    async def message(self, opcode: str, data: dict | None=None) -> None:
        async with self._queue_condition:
            self._send_queue.append((opcode, data))
            self._queue_condition.notify()

    async def priority_message(self, opcode: str, data: dict | None=None) -> None:
        async with self._queue_condition:
            self._send_queue.appendleft((opcode, data))
            self._queue_condition.notify()

    async def _send_message(self, opcode: str, data: dict | None=None) -> None:
        try:
            if data:
                await self.connection.send(f"{opcode} {json.dumps(data)}")
            else:
                await self.connection.send(opcode)

        except Exception as e:
            print("could not send data to server")
            print(e)

    async def read(self) -> str | None:
        try:
            return await self.connection.recv()

        except Exception as e:
            print("could not read from stream ...")
            print(e)
            
    async def receive(self) -> str:
        async with self._recv_condition:
            while not self._recv_queue:
                await self._recv_condition.wait()
    
            return self._recv_queue.popleft()

    async def get_api_ticket(self) -> str:
        return await get_ticket(self.bot.config.account, self.bot.config.password)

    def status(self) -> str:
        return self.connection.state.name

    async def _send_loop(self) -> None:
        while True:
            async with self._queue_condition:
                while not self._send_queue:
                    await self._queue_condition.wait()

                opcode, data = self._send_queue.popleft()
                print(len(self._send_queue), opcode)
                
            await self._send_message(opcode, data)
            await asyncio.sleep(1.0)
            
    async def _recv_loop(self) -> None:
        while True:
            message_str = await self.connection.recv()
            print(message_str)
            message = _parsed(*message_str.split(" ", 1))
            print(message)
            
            async with self._recv_condition:
                if message[0] == opcode.PING:
                    self._recv_queue.appendleft(message)
                else:
                    self._recv_queue.append(message)
                self._recv_condition.notify()
