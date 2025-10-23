from framework import Api
from framework import opcode
import json


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
        
    async def connect(self) -> None:
        await self.connect(self.config.server, self.config.port)
        await self.identify()

    async def _restart(self) -> None:
        print("MSG: restart chatbot")
        await self.connect()
        await self.bot.channel_manager.rejoin_channels()
        self.restarts += 1

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

    
