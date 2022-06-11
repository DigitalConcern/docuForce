import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import DialogRegistry
from config import API_TOKEN


class MyBot:
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    registry = DialogRegistry(dp)

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
