import asyncio
from threading import Thread
from multiprocessing import Process
from aiohttp import web
import functools




def Webserver(bot):
    loop = asyncio.new_event_loop()
    
    def __validate_secret(request):
        secret = request.headers.get("secret")
        if secret == bot.config.webserver['secret']:
            return True
        else:
            raise web.HTTPForbidden()
            return False
    
    async def sysinfo(request):
        return web.Response(text=bot._sysinfo())

    async def admins(request):
        string = "\nOwner: [user]"+bot.owner+"[/user]\n"
        string += "Admins:\n"
        for admin in bot.admins:
            string += "[user]"+admin+"[/user]\n"
            
        return web.Response(text=string)
    
    async def cows(request):        
        if (__validate_secret(request)):
            ranch = bot.plugin_loader.plugins['Ranch']
            secret = request.headers.get("secret")
        
            return web.Response(text=str({'response' : ranch.list_all_cows()}))
            
    async def workers(request):
        pass
    
    async def save_settings(request):
        secret = request.headers.get("secret")
        
        if secret == bot.config.webserver['secret']:
            await bot._save_all_settings(bot.config.owner)
            raise web.HTTPSuccessful()
            return web.Response("{'response: 'success'")
        else:
            raise web.HTTPForbidden()
    
    
    app = web.Application()
    app.add_routes([web.get('/', sysinfo)])
    app.add_routes([web.get('/admins', admins)])
    app.add_routes([web.get('/ranch/cows', cows)])
    app.add_routes([web.get('/ranch/workers', workers)])
    
    app.add_routes([web.post('/save', save_settings)])
    
    handler = app.make_handler()
    server = loop.create_server(handler, host=bot.config.webserver['host'], port=bot.config.webserver['port'])
    
    
    def aiohttp_server():
        loop.run_until_complete(server)
        loop.run_forever()
    
    
    ranch = Thread(target=aiohttp_server)
    ranch.start()