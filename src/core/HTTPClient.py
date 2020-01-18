import aiohttp
import re

class HTTPClient():
    
    @staticmethod
    async def get_cookies(url, endpoint):
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as s:
            async with s.get(url + endpoint) as response:
                cookies = s.cookie_jar.filter_cookies(url)                    
                return cookies
    
    @staticmethod
    async def get(endpoint, headers={}, cookies={}):  
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            async with session.get(endpoint) as response:
                assert response.status == 200
                return await response.text()
            
            
    @staticmethod
    async def get_csrf_token(endpoint):
        html = await HTTPClient.get(endpoint)
        return HTTPClient.__get_regex(html)
    
    
    @staticmethod
    def __get_regex(text, pattern = 'name="csrf-token" content="(.+)"'):
        return re.search(pattern, text).group(1).strip()
    
    @staticmethod
    async def post(endpoint, data={}, headers={}, json=True):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(endpoint, data=data) as response:
                assert response.status == 200
                if json:                    
                    return await response.json()
                else:
                    return await response.text()

    @staticmethod
    async def get_login_cookie(endpoint, data={}, headers={}):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(endpoint, data=data) as response:
                assert response.status == 200
                return response.cookies























