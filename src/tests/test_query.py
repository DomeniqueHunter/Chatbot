#!/usr/bin/python3
import unittest, sys
import re
sys.path.append('..')
sys.path.append('../core')

import asyncio

from framework.api import get_ticket
from framework.lib.config import Config
from framework.lib.httpclient import HTTPClient


def async_test(coro):

    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))

    return wrapper


def get_regex(text, pattern='Views<\/span>:([0-9]+)'):
    return re.search(pattern, text).group(1).strip()


def reduce (text):
    return text.replace('\n', "").replace('\r', "").replace("\t", "").replace(" ", "")


class TestCase(unittest.TestCase):

    @async_test
    async def setUp(self):
        self.config = Config("../config.json", False)
        self.ticket = await get_ticket(self.config.account, self.config.password)

    @async_test
    async def test_get_ticket(self):
        print ("ticket: {}".format(self.ticket))

    @async_test
    async def test_get_user_data(self):
        name = "Troya Williams"
        data = {'account': self.config.account, 'ticket': self.ticket, 'name': name}
        user_data = await HTTPClient.post("https://www.f-list.net/json/api/character-data.php", data=data)
        print(f"{user_data['name']}: {user_data['views']}")
        self.assertEqual(name, user_data["name"])

    @async_test
    async def test_get_user_data2(self):
        name = "Domenique Hunter"
        data = {'account': self.config.account, 'ticket': self.ticket, 'name': name}
        user_data = await HTTPClient.post("https://www.f-list.net/json/api/character-data.php", data=data)
        print(f"{user_data['name']}: {user_data['views']}")
        self.assertEqual(name, user_data["name"])

    @async_test
    async def test_view_not_logged_in(self):
        url = "https://www.f-list.net"
        endpoint = "/c/domenique hunter/"
        cookies = await HTTPClient.get_cookies(url, endpoint)
        html = await HTTPClient.get(url + endpoint, cookies=cookies)
        views = get_regex(reduce(html), 'Views<\/span>:([0-9]+)')
        print(f"views: {views}")
        self.assertIsInstance(views, str, "view should be member of string")

    @async_test
    async def test_login(self):
        login_server = "https://www.f-list.net/action/script_login.php"
        csrf = await HTTPClient.get_csrf_token(login_server)

        data = {'username': self.config.account, 'password': self.config.password, 'csrf_token': csrf}

        cookies = await HTTPClient.get_login_cookie(login_server, data)
        
        url = "https://www.f-list.net"
        endpoint = f"/c/{self.config.owner}"
        html = await HTTPClient.get(url + endpoint, cookies=cookies)

        views = get_regex(reduce(html), 'Views<\/span>:([0-9]+)')
        bookmarked_by = get_regex(reduce(html), 'Bookmarkedby<\/span>:([0-9]+)')

        print(f"Views: {views}")
        self.assertIsInstance(views, str, "view should be member of string")

        print(f"Bookmarked by: {bookmarked_by}")
        self.assertIsInstance(bookmarked_by, str, "bookmarks should be member of string")

if __name__ == "__main__":
    unittest.main()  # run all tests
