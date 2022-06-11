from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ParseMode, CallbackQuery

from aiogram_dialog import ChatEvent, Dialog, DialogManager, Window, StartMode
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Start, Column, Select, Group
from aiogram_dialog.widgets.text import Const, Format

from bot import MyBot
from client import get_orgs_dict
from database import ActiveUsers


class OrgSG(StatesGroup):
    choose_org = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    orgs_dict = await get_orgs_dict(MyBot.access_token,
                                    MyBot.refresh_token)

    orgs_list = ""
    for key in orgs_dict.keys():
        orgs_list += f'{key}. {orgs_dict[key][0]}\n'
    dialog_manager.current_context().dialog_data["organization_dict"] = orgs_dict

    return {
        'organization_keys': orgs_dict.keys(),
        'organization_list': orgs_list,
    }


async def on_org_clicked(c: CallbackQuery, select: Select, manager: DialogManager, item_id: str):
    org_uuid = manager.current_context().dialog_data["organization_dict"][item_id][1]

    await ActiveUsers.filter(user_id=c.from_user.id).update(organization=org_uuid)

    await manager.done()

org_dialog = Dialog(
    Window(
        Format("Выберите организацию\n\n{organization_list}"),
        Group(Select(
            Format("{item}"),
            items="organization_keys",
            item_id_getter=lambda x: x,
            id="orgs",
            on_click=on_org_clicked
        ), width=4),
        state=OrgSG.choose_org,
        getter=get_data,
        parse_mode=ParseMode.HTML
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)

MyBot.register_dialogs(org_dialog)
