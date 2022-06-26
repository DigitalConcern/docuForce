import asyncio
from asyncio import CancelledError

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import DialogManager, StartMode

from bot import MyBot
from client import get_access
from database import ActiveUsers, Stats
from notifications import loop_notifications_8hrs, loop_notifications_instant
from .auth_dialog import AuthSG
from .messages_dialog import MessagesSG
from .tasks_dialog import TasksSG
from .list_doc_dialog import ListDocSG
from .settings_dialog import SettingsSG


class MenuSG(StatesGroup):
    choose_action = State()


async def start_notifications(user_id: int, manager: DialogManager):
    eight_hour_notification = \
        (await ActiveUsers.filter(user_id=user_id).values_list("eight_hour_notification", flat=True))[0]
    instant_notification = \
        (await ActiveUsers.filter(user_id=user_id).values_list("instant_notification", flat=True))[0]
    if not eight_hour_notification and not instant_notification:
        await ActiveUsers.filter(user_id=user_id).update(instant_notification=True)
        await loop_notifications_instant(user_id=user_id, manager=manager.bg())
    elif eight_hour_notification:
        try:
            for task in asyncio.all_tasks():
                if task.get_name() == str(user_id):
                    task.cancel()
        except CancelledError:
            pass
        await loop_notifications_8hrs(user_id=user_id, manager=manager.bg())
    elif instant_notification:
        try:
            for task in asyncio.all_tasks():
                if task.get_name() == str(user_id):
                    task.cancel()
        except CancelledError:
            pass
        await loop_notifications_instant(user_id=user_id, manager=manager.bg())


async def tasks(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await get_access(refresh_token=(await ActiveUsers.filter(user_id=m.from_user.id).values_list("refresh_token"))[0],user_id=m.from_user.id)
        await start_notifications(user_id=m.from_user.id, manager=dialog_manager)

        command_tasks = (await Stats.filter(id=0).values_list("command_tasks", flat=True))[0]
        await Stats.filter(id=0).update(command_tasks=command_tasks + 1)

        await dialog_manager.start(TasksSG.choose_action, mode=StartMode.RESET_STACK)


async def document_search(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await get_access(
            refresh_token=(await ActiveUsers.filter(user_id=m.from_user.id).values_list("refresh_token"))[0],
            user_id=m.from_user.id)
        await start_notifications(user_id=m.from_user.id, manager=dialog_manager)

        command_search = (await Stats.filter(id=0).values_list("command_search", flat=True))[0]
        await Stats.filter(id=0).update(command_search=command_search + 1)

        await dialog_manager.start(ListDocSG.find, mode=StartMode.RESET_STACK)


async def document_list(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await get_access(
            refresh_token=(await ActiveUsers.filter(user_id=m.from_user.id).values_list("refresh_token"))[0],
            user_id=m.from_user.id)
        await start_notifications(user_id=m.from_user.id, manager=dialog_manager)

        command_documents = (await Stats.filter(id=0).values_list("command_documents", flat=True))[0]
        await Stats.filter(id=0).update(command_documents=command_documents + 1)

        await dialog_manager.start(ListDocSG.choose_action, mode=StartMode.RESET_STACK)


async def settings(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await start_notifications(user_id=m.from_user.id, manager=dialog_manager)

        await dialog_manager.start(SettingsSG.choose_action, mode=StartMode.RESET_STACK)


async def messages(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await get_access(
            refresh_token=(await ActiveUsers.filter(user_id=m.from_user.id).values_list("refresh_token"))[0],
            user_id=m.from_user.id)
        await start_notifications(user_id=m.from_user.id, manager=dialog_manager)

        command_messages = (
            await Stats.filter(id=0).values_list("command_messages", flat=True))[0]
        await Stats.filter(id=0).update(command_messages=command_messages + 1)

        await dialog_manager.start(MessagesSG.choose_action, mode=StartMode.RESET_STACK)


MyBot.register_handler(method=tasks, commands="tasks", state="*")
MyBot.register_handler(method=document_search, commands="search", state="*")
MyBot.register_handler(method=document_list, commands="documents", state="*")
MyBot.register_handler(method=settings, commands="settings", state="*")
MyBot.register_handler(method=messages, commands="messages", state="*")
