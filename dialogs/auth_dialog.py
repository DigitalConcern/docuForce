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
from .menu_dialog import MenuSG


class AuthSG(StatesGroup):
    login = State()
    password = State()


async def start(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
        dialog_manager.current_context().dialog_data["id"] = m.from_user.id
    else:
        await dialog_manager.start(MenuSG.choose_action)


MyBot.register_handler(method=start, commands="start", state="*")


async def login_handler(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data["login"] = m.text
    await dialog_manager.switch_to(AuthSG.password)


async def password_handler(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data["password"] = m.text

    resp = await sign_in(login=dialog_manager.current_context().dialog_data["login"],
                         password=dialog_manager.current_context().dialog_data["password"])

    if resp:
        user_org_id = await get_user_oguid(access_token=resp[0])
        await ActiveUsers(user_id=dialog_manager.current_context().dialog_data["id"],
                          user_org_id=user_org_id,
                          login=dialog_manager.current_context().dialog_data["login"],
                          password=dialog_manager.current_context().dialog_data["password"],
                          refresh_token=resp[1],
                          access_token=resp[0]
                          ).save()
        await dialog_manager.done()
        await MyBot.bot.send_message(m.from_user.id, "Вы успешно авторизировались!")

        await dialog_manager.start(MenuSG.choose_action)
        await dialog_manager.start(OrgSG.choose_org)
    else:
        await MyBot.bot.send_message(m.from_user.id, "Неверный логин или пароль\nПопробуйте еще раз!", parse_mode="HTML")
        await dialog_manager.switch_to(AuthSG.login)


auth_dialog = Dialog(
    Window(
        Const("Введите логин"),
        MessageInput(login_handler),
        state=AuthSG.login
    ),
    Window(
        Const("Введите пароль"),
        MessageInput(password_handler),
        state=AuthSG.password
    ),
    launch_mode=LaunchMode.ROOT
)
