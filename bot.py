import base64
import logging
from typing import IO, Union, Optional

import requests
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import DialogRegistry
from aiogram_dialog.manager.protocols import MediaAttachment, MediaId
from aiogram_dialog.message_manager import MessageManager

from config import API_TOKEN

class SuperMesssageManager(MessageManager):
    async def get_media_source(self, media: MediaAttachment) -> Union[IO, str]:
        if media.file_id:
            return media.file_id.file_id
        if media.url:
            response=requests.get(url=media.url,headers=media.url_headers)
            return base64.b64decode(response.text)
        else:
            return open(media.path, "rb")

    # async def get_media_id(message: Message) -> Optional[MediaId]:
    #     media = (
    #             message.audio or
    #             message.animation or
    #             message.document or
    #             (message.photo[-1] if message.photo else None) or
    #             message.video
    #     )
    #     if not media:
    #         return None
    #     return MediaId(
    #         file_id=media.file_id,
    #         file_unique_id=media.file_unique_id,
    #     )

class MyBot:
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    our_cool_mess=SuperMesssageManager()
    registry = DialogRegistry(dp,message_manager=our_cool_mess)

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
