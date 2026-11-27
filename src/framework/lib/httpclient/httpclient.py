import aiohttp
import re
from http.cookies import SimpleCookie
from yarl import URL


class HTTPClient():
    
    @staticmethod
    async def get_cookies(url:str, endpoint:str) -> aiohttp.CookieJar:
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as s:
            async with s.get(url + endpoint):
                cookies = s.cookie_jar.filter_cookies(URL(url))                    
                return cookies
    
    # todo: type dict
    @staticmethod
    async def get(endpoint:str, headers:dict=None, cookies=None):
        headers = headers or {}
        cookies = cookies or {}
        
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            async with session.get(endpoint) as response:
                assert response.status == 200
                return await response.text()
            
    @staticmethod
    async def get_csrf_token(endpoint:str) -> str:
        html = await HTTPClient.get(endpoint)
        return HTTPClient.__get_regex(html)
    
    @staticmethod
    def __get_regex(text:str, pattern:str='name="csrf-token" content="(.+)"') -> str:
        return re.search(pattern, text).group(1).strip()
    
    # todo: type dict
    @staticmethod
    async def post(endpoint:str, data:dict=None, headers:dict=None, json:bool=True) -> dict | str:
        data = data or {}
        headers = headers or {}
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(endpoint, data=data) as response:
                assert response.status == 200
                if json: 
                    return await response.json()
                else:
                    return await response.text()

    # todo: type dict
    @staticmethod
    async def get_login_cookie(endpoint:str, data:dict=None, headers:dict=None) -> SimpleCookie:
        data = data or {}
        headers = headers or {}

        async with aiohttp.ClientSession(headers=headers, cookie_jar=aiohttp.CookieJar()) as session:
            async with session.post(endpoint, data=data) as response:
                response.raise_for_status()
                cookies = session.cookie_jar.filter_cookies(URL(endpoint))

        if not cookies:
            raise RuntimeError(f"Login failed: no cookies received from {endpoint}")
        return cookies

