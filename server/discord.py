from time import sleep
from typing import Generator, List

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from server.consts import *
from server.exceptions import ChatNotFoundException


class DiscordServer:

    def __init__(self, server_name: str, browser: WebDriver):
        self._server_name = server_name
        self._browser = browser

    def login(self):
        self._browser.get(DISCORD_LOGIN_URL)
        print("Login not implemented, press any key after you have successfully logged in!")
        input()
        self._go_in_server()

    def _go_in_server(self):
        servers = self._browser.find_element(By.XPATH, SERVERS_DIV_XPATH)
        for element in servers.find_elements(By.CLASS_NAME, SERVER_EXTERNAL_DIV_CLASS):
            name_class = element.find_element(By.CLASS_NAME, SERVER_INTERNAL_DIV_CLASS)
            name = name_class.get_attribute(SERVER_NAME_ATTRIBUTE)
            if name == self._server_name:
                element.click()

    def chat_messages_gen(self, chat_name: str) -> Generator[str, None, None]:
        self._get_in_chat(chat_name)
        messages = self._get_all_messages()
        last_message = messages[-1].text
        one_before_message = "RANDOM STRING THAT HOPEFULLY WONT BE SENT"
        while True:
            messages = self._get_all_messages()
            for message in self._get_unread_exception_loop(last_message, one_before_message, messages):
                yield message
                one_before_message = last_message
                last_message = message

    def _get_all_messages(self) -> List[WebElement]:
        messages = self._browser.find_elements(By.XPATH, MESSAGES_LIST)
        while len(messages) == 0:
            messages = self._browser.find_elements(By.XPATH, MESSAGES_LIST)
        return messages

    def _get_unread_exception_loop(self, last_message: str, one_before_message: str,
                                   messages: List[WebElement]) -> List[str]:
        try:
            return self._get_unread_messages(last_message, one_before_message, messages)
        except StaleElementReferenceException:
            messages = self._get_all_messages()
            return self._get_unread_exception_loop(last_message, one_before_message, messages)

    def _get_unread_messages(self, last_message: str, one_before_message: str,  messages: List[WebElement]) -> List[str]:
        unread_messages = []
        for id in range(len(messages) - 1, 0, -1):
            if messages[id].text == last_message or messages[id].text == one_before_message:
                break
            unread_messages.append(messages[id].text)
        return unread_messages[::-1]

    def _get_in_chat(self, chat_name: str):
        chats = self._browser.find_elements(By.CLASS_NAME, CHANNEL_CLASS)
        for chat in chats:
            if chat.get_attribute(CHANNEL_NAME_ATTRIBUTE) == chat_name:
                chat.click()
                sleep(3)
                return
        raise ChatNotFoundException()
