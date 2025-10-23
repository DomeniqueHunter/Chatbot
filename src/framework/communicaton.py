from framework.api import get_ticket
from framework.lib.config import Config
from framework import opcode
import json
import websockets.client


class Communication:
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.config:Config = self.bot.config
        self.connection = None
        
    async def identify(self) -> None:
        data = {
            'method': 'ticket',
            'ticket': await self.get_api_ticket(),
            'account': str(self.config.account),
            'character': str(self.config.character),
            'cname': "Python Client",
            'cversion': self.bot.version,
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

    async def message(self, opcode:str, data:dict=None) -> None:
        try:
            if data:
                await self.connection.send(f"{opcode} {json.dumps(data)}")
                
            else:
                await self.connection.send(opcode)

        except Exception as e:
            print("could not send data to server")
            print(e)

    async def read(self) -> str:
        try:
            return await self.connection.recv()

        except Exception as e:
            print("could not read from stream ...")
            print(e)
            
    async def get_api_ticket(self) -> str:
        return await get_ticket(self.bot.config.account, self.bot.config.password)
    
    def status(self) -> str:
        return self.connection.state.name
    
