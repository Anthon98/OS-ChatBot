# -*- encoding: utf-8 -*-

# Dependencies
import requests
import argparse
import logging as logger
import json

from pprint import pprint
from bs4 import BeautifulSoup
from typing import Tuple
from configparser import ConfigParser

logger.basicConfig(level=logger.DEBUG)


class ChatBot:
    def __init__(self: '__main__.ChatBot', username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.handle()

    def __repr__(self: '__main__.ChatBot') -> str:
        # To be made.
        return '__repr__ for ChatBot'

    def __str__(self: '__main__.ChatBot') -> str:
        # To be made.
        return '__str__ for ChatBot'

    def login(self: '__main__.ChatBot', session) -> Tuple['requests.sessions.Session', str]:
        logger.info("Logging in...")
        url = 'https://onlinesequencer.net/forum/member.php'
        # Dummy call to get the post key. (get or post here wont matter)
        get_my_post_key = session.get(url)

        # Generate an lxml format and parse through with bs4, this isn't a request
        # It just finds and gets values much like regex in the actual response.
        # Because usually these 'challenge' validator types are embedded in the page.
        # Not bad practice by any means.
        soup = BeautifulSoup(get_my_post_key.text, 'lxml')
        my_post_key = soup.find(
            'input', attrs={'name': 'my_post_key', 'type': 'hidden'}).get('value')

        data = {
            'action': 'do_login',
            'remember': 'yes',
            'url': '/ajax/login.php',
            'username': self.username,
            'password': self.password,
            'my_post_key': my_post_key,
        }

        response = session.post(url, data=data)
        response_json = json.loads(response.text)
        my_post_key = response_json['post_key']

        # Format our cookie for the header.
        cookie = ''
        for k, v in session.cookies.items():
            cookie += '%s=%s; ' % (k, v)

        header = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': '0',
            'Host': 'onlinesequencer.net',
            'User-Agent': 'PostmanRuntime/7.28.2',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cookie': cookie
        }

        # Replace default headers with our new one.
        session.headers = header

        return session, my_post_key

    def send_message(self: '__main__.ChatBot', session: 'requests.sessions.Session', my_post_key: str, message: str) -> None:
        send_chat = 'https://onlinesequencer.net/forum/xmlhttp.php?action=ajaxchat_send'

        chat_data = {
            'my_post_key': my_post_key,
            'context': '0',
            'message': message,
        }

        send = session.post(send_chat, data=chat_data)
        pprint(send.text)

    def handle(self: '__main__.ChatBot') -> None:
        # Due to 302 redirect we need to use sessions.
        with requests.session() as session:
            session, my_post_key = self.login(session=session)

            for _ in range(1):
                inpt = str(input("Chat Message: "))

                self.send_message(session=session,
                                  my_post_key=my_post_key, message=inpt)


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
