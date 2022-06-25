import asyncio
from asyncio import CancelledError

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ParseMode

from aiogram_dialog import ChatEvent, Dialog, DialogManager, Window, StartMode
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Start, Column, Select, Group
from aiogram_dialog.widgets.text import Const, Format

from client import sign_in, get_user_oguid
from bot import MyBot
from database import ActiveUsers
from .org_dialog import OrgSG
from notifications import loop_notifications_8hrs, loop_notifications_instant


class AuthSG(StatesGroup):
    login = State()
    password = State()


async def login_handler(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data["login"] = m.text
    dialog_manager.current_context().dialog_data["login_id"] = m.message_id
    await dialog_manager.switch_to(AuthSG.password)


async def password_handler(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data["password"] = m.text
    dialog_manager.current_context().dialog_data["password_id"] = m.message_id
    dialog_manager.current_context().dialog_data["id"] = m.from_user.id

    resp = await sign_in(login=dialog_manager.current_context().dialog_data["login"],
                         password=dialog_manager.current_context().dialog_data["password"])

    await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id,
                                   message_id=dialog_manager.current_context().dialog_data["login_id"])
    await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id,
                                   message_id=dialog_manager.current_context().dialog_data["password_id"])

    if resp:
        user_org_id = await get_user_oguid(access_token=resp[0], refresh_token=resp[1], user_id=m.from_user.id)
        await ActiveUsers(user_id=dialog_manager.current_context().dialog_data["id"],
                          user_org_id=user_org_id,
                          login=dialog_manager.current_context().dialog_data["login"],
                          password=dialog_manager.current_context().dialog_data["password"],
                          refresh_token=resp[1],
                          access_token=resp[0]
                          ).save()

        await dialog_manager.done()
        await MyBot.bot.send_message(m.from_user.id, "Вы успешно авторизировались! ✅")

        users = (await ActiveUsers.all().values_list("users", flat=True))[0]
        await ActiveUsers.all().update(users=users + 1)

        await loop_notifications_instant(user_id=m.from_user.id, manager=dialog_manager)

        await dialog_manager.start(OrgSG.choose_org)
    else:
        await MyBot.bot.send_message(m.from_user.id, "Неверный логин или пароль ❌\nПопробуйте еще раз!",
                                     parse_mode="HTML")
        await dialog_manager.switch_to(AuthSG.login)


auth_dialog = Dialog(
    Window(
        Const("Введите логин 🔒"),
        MessageInput(login_handler),
        state=AuthSG.login
    ),
    Window(
        Const("Введите пароль 🔒"),
        MessageInput(password_handler),
        state=AuthSG.password
    ),
    launch_mode=LaunchMode.ROOT
)
