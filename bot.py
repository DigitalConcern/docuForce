import base64
import logging
from io import BytesIO
from typing import IO, Union, Optional

import requests
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import DialogRegistry
from aiogram_dialog.manager.protocols import MediaAttachment, MediaId
from aiogram_dialog.message_manager import MessageManager

from config import API_TOKEN


class SuperMesssageManager(MessageManager):
    async def get_media_source(self, media: MediaAttachment) -> Union[IO, str]:
        if media.file_id:
            return media.file_id.file_id
        if media.url:
            response = requests.get(url=media.url, headers=media.url_headers)
            return BytesIO(base64.b64decode(response.text))
        else:
            return open(media.path, "rb")


class MyBot:
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    our_cool_mess = SuperMesssageManager()
    registry = DialogRegistry(dp, message_manager=our_cool_mess)

    access_token = ""
    refresh_token = ""

    @classmethod
    async def run_bot(cls):
        logging.basicConfig(level=logging.INFO)
        await cls.dp.start_polling()

    @classmethod
    def register_handler(cls, **kwargs):
        cls.dp.register_message_handler(kwargs["method"], commands=kwargs["commands"])

    @classmethod
    def register_dialogs(cls, *args):
        for dialog in args:
            cls.registry.register(dialog)
