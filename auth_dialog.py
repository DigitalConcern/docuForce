from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ParseMode

from aiogram_dialog import ChatEvent, Dialog, DialogManager, Window, StartMode
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Start, Column, Select, Group
from aiogram_dialog.widgets.text import Const, Format

from auth import sign_in, get_access, get_orgs_dict
from bot import MyBot
from database import ActiveUsers


class AuthSG(StatesGroup):
    login = State()
    password = State()
    organization = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    return {
        'id': dialog_manager.current_context().dialog_data.get("id", None),
        'login': dialog_manager.current_context().dialog_data.get("login", None),
        'password': dialog_manager.current_context().dialog_data.get("password", None),
        'organization_choosed': dialog_manager.current_context().dialog_data.get("organization_choosed", None),
        'organization_keys': dialog_manager.current_context().dialog_data.get("organization_keys", None),
        'organization_uuid': dialog_manager.current_context().dialog_data.get("organization_uuid", None),
        'organization_list': dialog_manager.current_context().dialog_data.get("organization_list", None),
        'access_token': dialog_manager.current_context().dialog_data.get("access_token", None),
        'refresh_token': dialog_manager.current_context().dialog_data.get("refresh_token", None),
    }


async def start(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await MyBot.bot.send_message(m.from_user.id, "Здравствуйте!\nПройдите авторизацию!", parse_mode="HTML")
        await dialog_manager.start(AuthSG.login, mode=StartMode.RESET_STACK)
        dialog_manager.current_context().dialog_data["id"] = m.from_user.id
    # else:
    #     Если он есть то переходим в меню
    #     await dialog_manager.start(docsSG.menu, mode=StartMode.RESET_STACK)
    #     dialog_manager.current_context().dialog_data["name"] = \
    #         (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_name"))[0]
    #     dialog_manager.current_context().dialog_data["grade"] = \
    #         (await ActiveUsers.filter(user_id=m.from_user.id).values_list("grade"))[0]


MyBot.register_handler(method=start, commands="start", state="*")

# async def set_org(m: Message, dialog_manager: DialogManager):
#     org_num = m.get_args()
#     if await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id"):
#         await ActiveUsers(user_id=dialog_manager.current_context().dialog_data["id"],
#                           login=dialog_manager.current_context().dialog_data["login"],
#                           password=dialog_manager.current_context().dialog_data["password"],
#                           organization=org_num
#                           ).save()
#     else:
#         await MyBot.bot.send_message(m.from_user.id, "Пожалуйста, пройдите сначала регистрацию", parse_mode="HTML")

# MyBot.register_handler(method=set_org, text="/setorg", state="*")


async def login_handler(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data["login"] = m.text
    await dialog_manager.switch_to(AuthSG.password)


async def password_handler(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data["password"] = m.text

    dialog_manager.current_context().dialog_data["access_token"], \
    dialog_manager.current_context().dialog_data["refresh_token"] = \
        await sign_in(dialog_manager.current_context().dialog_data["login"],
                dialog_manager.current_context().dialog_data["password"])

    orgs_dict = await get_orgs_dict(dialog_manager.current_context().dialog_data["access_token"])
    dialog_manager.current_context().dialog_data["organization_keys"] = list(orgs_dict.keys())

    orgs_lst = ""
    for key in dialog_manager.current_context().dialog_data["organization_keys"]:
        orgs_lst += f'{key}. {orgs_dict[key]}\n'
    dialog_manager.current_context().dialog_data["organization_list"] = orgs_lst

    await dialog_manager.switch_to(AuthSG.organization)


async def on_org_clicked(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    manager.current_context().dialog_data["organization_choosed"] = int(item_id)
    await ActiveUsers(user_id=manager.current_context().dialog_data["id"],
                      login=manager.current_context().dialog_data["login"],
                      password=manager.current_context().dialog_data["password"],
                      organization=manager.current_context().dialog_data["organization_choosed"]
                      ).save()

    await manager.done()


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
    Window(
        Format("Вы успешно авторизировались!\nВыберите организацию\n\n{organization_list}"),
        Group(Select(
            Format("{item}"),
            items="organization_keys",
            item_id_getter=lambda x: x,
            id="orgs",
            on_click=on_org_clicked
        ), width=4),
        state=AuthSG.organization,
        getter=get_data,
        parse_mode=ParseMode.HTML
    ),
    launch_mode=LaunchMode.ROOT
)

MyBot.register_dialogs(auth_dialog)