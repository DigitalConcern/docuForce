import base64
import logging
import pathlib
from io import BytesIO
from typing import IO, Union, Optional, Dict, Any

import requests
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType
from aiogram_dialog import DialogRegistry
from aiogram_dialog.manager.protocols import MediaId, DialogManager
from aiogram_dialog.message_manager import MessageManager
from aiogram_dialog.widgets.media import Media
from aiogram_dialog.widgets.when import WhenCondition

from config import API_TOKEN


class SuperMediaAttachment:
    def __init__(
            self,
            type: ContentType,
            url: Optional[str] = None,
            url_headers: Optional[str] = None,
            path: Optional[str] = None,
            file_id: Optional[MediaId] = None,
            **kwargs,
    ):
        if not (url or path or file_id):
            raise ValueError("Neither url nor path not file_id are provided")
        self.type = type
        self.url = url
        self.url_headers = url_headers
        self.path = path
        self.file_id = file_id
        self.kwargs = kwargs


class DynamicMedia(Media):
    def __init__(
            self,
            *,
            path: Optional[str] = None,
            url: Optional[str] = None,
            url_headers: Optional[str] = None,
            type: ContentType = ContentType.PHOTO,
            media_params: Dict = None,
            when: WhenCondition = None,
    ):
        super().__init__(when)
        if not (url or path):
            raise ValueError("Neither url nor path are provided")
        self.type = type
        self.path = path
        self.url = url
        self.url_headers = url_headers
        self.media_params = media_params or {}

    async def _render_media(
            self,
            data: Any,
            manager: DialogManager
    ) -> Optional[SuperMediaAttachment]:
        return SuperMediaAttachment(
            type=self.type,
            url=self.url.format_map(data),
            url_headers={"Access-Token": self.url_headers.format_map(data)},
            path=self.path,
            **self.media_params,
        )


class SuperMesssageManager(MessageManager):
    async def get_media_source(self, media: SuperMediaAttachment) -> Union[IO, str]:
        if media.file_id:
            return media.file_id.file_id
        if media.url:

            response = requests.get(url=media.url, headers=media.url_headers)
            if response.status_code != 200:
                return open(pathlib.Path("./resources/white.png"), "rb")
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
