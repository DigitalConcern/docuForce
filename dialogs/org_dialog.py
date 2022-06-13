import asyncio
import time

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ParseMode, CallbackQuery

from aiogram_dialog import ChatEvent, Dialog, DialogManager, Window, StartMode
from aiogram_dialog.manager.protocols import LaunchMode, BaseDialogManager
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Start, Column, Select, Group
from aiogram_dialog.widgets.text import Const, Format

from bot import MyBot
from client import get_orgs_dict
from database import ActiveUsers
from .menu_dialog import MenuSG


class OrgSG(StatesGroup):
    choose_org = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = list(await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token"))[0]
    refresh_token, access_token = data[0], data[1]

    orgs_dict = await get_orgs_dict(access_token, refresh_token)
    orgs_list = "Выберите организацию\n\n"
    for key in orgs_dict.keys():
        orgs_list += f'{key}. {orgs_dict[key][0]}\n'
    dialog_manager.current_context().dialog_data["organization_dict"] = orgs_dict
    # dialog_manager.current_context().dialog_data["organization_list"] = orgs_list

    return {
        'organization_keys': orgs_dict.keys(),
        'organization_list': dialog_manager.current_context().dialog_data.get("organization_list", orgs_list)
    }


async def on_org_clicked(c: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    org_uuid = dialog_manager.current_context().dialog_data["organization_dict"][item_id][1]
    org_name = dialog_manager.current_context().dialog_data["organization_dict"][item_id][0]

    await ActiveUsers.filter(user_id=c.from_user.id).update(organization=org_uuid)

    # dialog_manager.current_context().dialog_data["organization_list"] = f"Организация\n{org_name}\nуспешно выбрана!"
    # await dialog_manager.bg().update({"organization_list": f"Организация\n{org_name}\nуспешно выбрана!"}) # МОЖНО ТАК

    # сделал через сообщение, тк стартует меню, а это ROOT диалог, следовательно стек ресетается и функции выше
    # ничего не меняют

    await MyBot.bot.send_message(c.from_user.id, f"Организация\n{org_name}\nуспешно выбрана!")
    await dialog_manager.start(MenuSG.choose_action)

org_dialog = Dialog(
    Window(
        Format("{organization_list}"),
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
