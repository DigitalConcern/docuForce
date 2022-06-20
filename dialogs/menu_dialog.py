import asyncio
from asyncio import CancelledError

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from bot import MyBot
from database import ActiveUsers
from notifications import loop_notifications_8hrs, loop_notifications_instant
from .auth_dialog import AuthSG
from .tasks_dialog import TasksSG
from .list_doc_dialog import ListDocSG
from .settings_dialog import SettingsSG


class MenuSG(StatesGroup):
    choose_action = State()


# menu_dialog = Dialog(
#     Window(
#         StaticMedia(
#              path="resources/logo.png",
#              type=ContentType.PHOTO
#         ),
#         Start(Const("Мои задачи"), id="tasks", state=TasksSG.choose_action),
#         Start(Const("Поиск документа"), id="search", state=ListDocSG.find),
#         Start(Const("Список документов"), id="list", state=ListDocSG.choose_action),
#         Start(Const("Настройки"), id="settings", state=SettingsSG.choose_action),
#         Start(Const("Сообщения"), id="messages", state=MessagesSG.choose_action),
#         state=MenuSG.choose_action
#     ),
#     launch_mode=LaunchMode.ROOT
# )

async def tasks(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(TasksSG.choose_action, mode=StartMode.RESET_STACK)


async def document_search(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(ListDocSG.find, mode=StartMode.RESET_STACK)


async def document_list(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(ListDocSG.choose_action, mode=StartMode.RESET_STACK)


async def settings(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(SettingsSG.choose_action, mode=StartMode.RESET_STACK)


async def messages(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(SettingsSG.choose_action, mode=StartMode.RESET_STACK)


MyBot.register_handler(method=tasks, commands="tasks", state="*")
MyBot.register_handler(method=document_search, commands="search", state="*")
MyBot.register_handler(method=document_list, commands="documents", state="*")
MyBot.register_handler(method=settings, commands="settings", state="*")
MyBot.register_handler(method=messages, commands="messages", state="*")
