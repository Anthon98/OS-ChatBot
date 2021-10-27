# -*- encoding: utf-8 -*-

# Dependencies
import requests
import argparse
import logging as logger
import json
import time
import re

from pprint import pprint
from bs4 import BeautifulSoup
from typing import Tuple
from configparser import ConfigParser

logger.basicConfig(level=logger.DEBUG)


class ChatBot:
    def __init__(self: '__main__.ChatBot', username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.urls = {
            'index': 'https://onlinesequencer.net/forum/index.php',
            'login': 'https://onlinesequencer.net/ajax/login.php',
            'member': 'https://onlinesequencer.net/forum/member.php',
            'send_chat': 'https://onlinesequencer.net/forum/xmlhttp.php?action=ajaxchat_send',
        }
        self.handle()

    def __repr__(self: '__main__.ChatBot') -> str:
        # To be made.
        return '__repr__ for ChatBot'

    def __str__(self: '__main__.ChatBot') -> str:
        # To be made.
        return '__str__ for ChatBot'

    def fetch_my_post_key(self: '__main__.ChatBot') -> None:
        # We need the default headers for the validation call.
        self.session.headers = self.default_header
        get_my_post_key = self.session.get(self.urls['login'])

        if not get_my_post_key.text == "false":
            response_json = json.loads(get_my_post_key.text)
            self.my_post_key = response_json['post_key']
        else:
            get_my_post_key = self.session.get(self.urls['index'])
            self.my_post_key = re.search('var my_post_key = "(.*)";',
                                         get_my_post_key.text).group(1)

        logger.info('Current validated my_post_key: %s' % self.my_post_key)

    def login(self: '__main__.ChatBot', session) -> Tuple['requests.sessions.Session', str]:
        logger.info("Logging in...")

        self.session = session
        self.default_header = self.session.headers
        self.fetch_my_post_key()

        data = {
            'action': 'do_login',
            'remember': 'yes',
            'url': '/ajax/login.php',
            'username': self.username,
            'password': self.password,
            'my_post_key': self.my_post_key,
        }

        print(data['my_post_key'])

        # In case of an invalid my_post_key, this will fail.

        try:
            response = self.session.post(self.urls['member'], data=data)
            response_json = json.loads(response.text)
            self.my_post_key = response_json['post_key']
        except Exception as e:
            logger.info("TEST???")
            logger.error(e)

        # Format our cookie for the header.
        self.cookie = ''
        for k, v in self.session.cookies.items():
            self.cookie += '%s=%s; ' % (k, v)

        header = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': '0',
            'Host': 'onlinesequencer.net',
            'User-Agent': 'PostmanRuntime/7.28.2',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cookie': self.cookie
        }

        # Replace default headers with our new one.
        self.main_header = header
        self.session.headers = self.main_header

    def send_message(self: '__main__.ChatBot', message: str) -> None:
        chat_data = {
            'my_post_key': self.my_post_key,
            'context': '0',
            'message': message,
        }

        self.session.post(self.urls['send_chat'], data=chat_data)
        # pprint(send.text)

    def handle(self: '__main__.ChatBot') -> None:
        # Due to 302 redirect we need to use sessions.
        with requests.session() as session:
            self.login(session=session)

            for _ in range(20):
                inpt = str(input("Chat Message: "))

                self.fetch_my_post_key()
                self.send_message(message=inpt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='OnlineSequencer ChatBot Help')
    # Args to be added.
    args = parser.parse_args()

    # Fetch username & password from the config file.
    file = 'chatbot.ini'
    config = ConfigParser()
    config.read(file)

    bot = ChatBot(username=config['account']['username'],
                  password=config['account']['password'])
