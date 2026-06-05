from framework.op_code_handler import OpCodeHandler

import time


class Bot(OpCodeHandler):

    def __init__(self, config, root_path="./"):
        super().__init__(config, root_path)        

    async def connect(self) -> None:
        await self.comm.start_sender()
        if await self.comm.connect():
            await self.comm.identify()
            await self.comm.start_receiver()

    async def _restart(self) -> None:
        await self.comm.stop()
        await self.connect()
        if self.comm.connection:
            await self.channel_manager.rejoin_channels()
        self.restarts += 1

    async def _prepare(self) -> None:
        await self.load_all_settings(self.owner)

        await self._order_list_of_open_private_channels()
        await self._order_list_of_official_channels()

        await self.join_default_channels(self.config.default_channels)

    async def _run (self) -> None:
        while True:
            if self.comm.connection != None and self.comm.status() == "OPEN":
                data = await self.comm.receive()

                await self.dispatcher(*data)

                if self.stop_impulse:
                    print("FULL STOP")
                    exit()

            else:
                print(f"!!!!!!!! RECONNECT ({self.restarts+1}) !!!!!!!!")
                await self.save_all_settings(self.owner)
                time.sleep(30)
                await self._restart()
                await self.load_all_settings(self.owner)

    def start(self) -> None:
        self.loop.run_until_complete(self.connect())
        self.loop.run_until_complete(self._prepare())
        self.loop.run_until_complete(self._run())

        self.loop.run_forever()

