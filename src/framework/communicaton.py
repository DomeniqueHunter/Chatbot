from framework import Api
from framework import opcode
import json
import websockets


class Comm:
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.config = self.bot.config
        
    async def identify(self) -> None:
        data = {
            'method': 'ticket',
            'ticket': await self.get_api_ticket(),
            'account': str(self.config.account),
            'character': str(self.config.charactername),
            'cname': "Python Client",
            'cversion': self.version,
        }
        await self._message(opcode.IDENTIFY, data)
        await self.read()
        
    async def connect(self, server:str, port:int) -> None:
        self.server = server
        self.port = port

        uri = self.config.protocol + self.server + self.config.endpoint

        try:
            self.connection = await websockets.client.connect(uri)
            print(f"connected to: {uri}")

        except Exception as e:
            print(f"could not connect to: {uri}")
            print(f"error: {e}")
            self.connection = None

    async def message(self, opcode:str, data=None) -> None:
        try:
            if data:
                await self.connection.send(f"{opcode} {json.dumps(data)}")

            else:
                await self.connection.send(opcode)

        except Exception as e:
            print("could not send data to server")
            print(e)
            exit()

    async def read(self) -> str:
        try:
            msg = await self.connection.recv()
            return msg

        except Exception as e:
            print("could not read from stream ...")
            print(e)
            
    async def get_api_ticket(self) -> str:
        return await Api.get_ticket(self.account, self.password)
    
