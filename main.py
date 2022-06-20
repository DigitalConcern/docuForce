import asyncio

import database
from bot import MyBot
from database import loop_db
from dialogs.org_dialog import org_dialog
from dialogs.auth_dialog import auth_dialog
from dialogs.menu_dialog import menu_dialog
from dialogs.tasks_dialog import tasks_dialog
from dialogs.view_doc_dialog import view_doc_dialog
from dialogs.settings_dialog import settings_dialog
from dialogs.list_doc_dialog import list_doc_dialog
from dialogs.messages_dialog import messages_dialog


async def main():
    MyBot.register_dialogs(auth_dialog)
    MyBot.register_dialogs(menu_dialog)
    MyBot.register_dialogs(org_dialog)
    MyBot.register_dialogs(tasks_dialog)
    MyBot.register_dialogs(view_doc_dialog)
    MyBot.register_dialogs(settings_dialog)
    MyBot.register_dialogs(list_doc_dialog)
    MyBot.register_dialogs(messages_dialog)

    await loop_db()
    await asyncio.sleep(2)
    for user_id in (await database.ActiveUsers.filter().values_list("user_id", flat=True)):
        await MyBot.bot.send_message(chat_id=user_id,text="Бот перезапущен! Чтобы продолжить работу - отправьте команду /start")
    await MyBot.run_bot()



if __name__ == '__main__':
    asyncio.run(main())
