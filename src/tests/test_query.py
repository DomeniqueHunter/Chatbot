#!/usr/bin/python3
import unittest, sys
import re
sys.path.append('..')
sys.path.append('../core')

import asyncio

from framework.api import Api
from framework.lib.config import Config
from framework.lib.httpclient import HTTPClient

def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper


def get_regex(text, pattern = 'Views<\/span>:([0-9]+)'):
    return re.search(pattern, text).group(1).strip()

def reduce (text):
    return text.replace('\n', "").replace('\r', "").replace("\t", "").replace(" ", "")

class TestCase(unittest.TestCase):
    
    @async_test
    async def setUp(self):
        self.config = Config("../config.json", False)
        self.ticket = await Api.get_ticket(self.config.account, self.config.password)
    
    @async_test
    async def test_get_ticket(self):
        print ("ticket: {}".format(self.ticket))
        
    @async_test
    async def test_get_user_data(self):
        name = "Troya Williams"
        data = {'account': self.config.account, 'ticket': self.ticket, 'name': name}
        user_data = await HTTPClient.post("https://www.f-list.net/json/api/character-data.php", data=data)
        assert name == user_data["name"]
        print (user_data["name"] + ": " + str(user_data["views"]))
        
    @async_test
    async def test_get_user_data2(self):
        name = "Domenique Hunter"
        data = {'account': self.config.account, 'ticket': self.ticket, 'name': name}
        user_data = await HTTPClient.post("https://www.f-list.net/json/api/character-data.php", data=data)
        user_data = await HTTPClient.post("https://www.f-list.net/json/api/character-data.php", data=data)
        assert name == user_data["name"]
        print (user_data["name"] + ": " + str(user_data["views"]))
        print (user_data)
        
    @async_test
    async def test_get_html(self):
        url = "https://www.f-list.net"
        endpoint = "/c/domenique hunter/"
        cookies =  await HTTPClient.get_cookies(url, endpoint)
        html = await HTTPClient.get(url+endpoint, cookies=cookies)
        #print (reduce(html))
        print (get_regex(reduce(html), 'Views<\/span>:([0-9]+)'))
      
    @async_test
    async def test_login(self):
        login_server = "https://www.f-list.net/action/script_login.php"
        csrf = await HTTPClient.get_csrf_token(login_server)
        print ("csrf: {}".format(csrf))
        
        data = {'username': self.config.account, 'password': self.config.password, 'csrf_token': csrf,
                'mime-type': ''}
        print (data)
        
        cookies = await HTTPClient.get_login_cookie(login_server, data)
        
        url = "https://www.f-list.net"
        endpoint = "/c/{}/".format(self.config.owner)
        #cookies =  await HTTPClient.get_cookies(url, endpoint)
        html = await HTTPClient.get(url+endpoint, cookies=cookies)
        views = get_regex(reduce(html), 'Views<\/span>:([0-9]+)')
        bookmarked_by = get_regex(reduce(html), 'Bookmarkedby<\/span>:([0-9]+)')
        
        print("Views: {}".format(views))
        print("Bookmarked by: {}".format(bookmarked_by))
        
        
        
        
        

if __name__ == "__main__":    
    unittest.main() # run all tests