from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from client import get_doc_dict
from database import ActiveUsers


class ViewDocSG(StatesGroup):
    choose_action = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "current_document_id",
                                                                                        "organization"))[0]
    refresh_token, access_token, current_document_id, organization = data[0], data[1], data[2], data[3]

    orgs_dict = await get_doc_dict(access_token, refresh_token, organization, current_document_id)
    orgs_list = "Выберите организацию\n\n"
    for key in orgs_dict.keys():
        orgs_list += f'{key}. {orgs_dict[key][0]}\n'
    dialog_manager.current_context().dialog_data["organization_dict"] = orgs_dict
    # dialog_manager.current_context().dialog_data["organization_list"] = orgs_list

    return {
        'organization_keys': orgs_dict.keys(),
        'organization_list': dialog_manager.current_context().dialog_data.get("organization_list", orgs_list)
    }


view_doc_dialog = Dialog(
    Window(
        Format("ass"),
        state=ViewDocSG.choose_action,
        getter=get_data
    ),
    launch_mode=LaunchMode.ROOT
)
