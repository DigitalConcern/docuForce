import asyncio
from asyncio import CancelledError

import tortoise.exceptions
from aiogram_dialog import DialogManager

from bot import MyBot
from database import loop_db, ActiveUsers, Stats
from dialogs.org_dialog import org_dialog
from dialogs.auth_dialog import auth_dialog
from dialogs.tasks_dialog import tasks_dialog
from dialogs.view_doc_dialog import view_doc_dialog
from dialogs.settings_dialog import settings_dialog
from dialogs.list_doc_dialog import list_doc_dialog
from dialogs.messages_dialog import messages_dialog
import dialogs.menu_dialog
import database
from notifications import loop_notifications_8hrs, loop_notifications_instant, start_notifications


async def main():
    MyBot.register_dialogs(auth_dialog)
    MyBot.register_dialogs(org_dialog)
    MyBot.register_dialogs(tasks_dialog)
    MyBot.register_dialogs(view_doc_dialog)
    MyBot.register_dialogs(settings_dialog)
    MyBot.register_dialogs(list_doc_dialog)
    MyBot.register_dialogs(messages_dialog)

    await loop_db()

    await asyncio.sleep(5)
    try:
        await Stats(id=0).save()
    except tortoise.exceptions.IntegrityError:
        pass
    for user_id in (await ActiveUsers.filter().values_list("user_id", flat=True)):
        await MyBot.bot.send_message(chat_id=user_id,
                                     text="Бот перезапущен! Чтобы продолжить работу - отправьте любую команду")
    await MyBot.run_bot()


if __name__ == '__main__':
    asyncio.run(main())
