from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
import os

from bot import MyBot
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
    dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data.get(
        "counter", 1)
    doc = await get_doc_dict(access_token, refresh_token, organization, current_document_id,
                             dialog_manager.current_context().dialog_data["counter"])
    import base64
    imgdata = base64.b64decode(doc["image_bin"])
    filename = f'{current_document_id}__{dialog_manager.current_context().dialog_data["counter"]}.jpg'
    with open(filename, 'wb+') as f:
        f.write(imgdata)
    f.close()
    dialog_manager.current_context().dialog_data["len"] = int(doc["len"])

    if dialog_manager.current_context().dialog_data["len"] == 1:
        dialog_manager.current_context().dialog_data["is_not_last"] = False
    # await MyBot.bot.send_photo(dialog_manager.event.from_user.id,imgdata)
    return {
        'filename': filename,
        'is_not_first': dialog_manager.current_context().dialog_data.get("is_not_first", False),
        'is_not_last': dialog_manager.current_context().dialog_data.get("is_not_last", True),
        'len': dialog_manager.current_context().dialog_data["len"],
        'counter': dialog_manager.current_context().dialog_data["counter"]
    }


async def switch_pages(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    match button.widget_id:
        case "plus":
            dialog_manager.current_context().dialog_data["counter"] += 1
            if dialog_manager.current_context().dialog_data["counter"] + 1 == \
                    dialog_manager.current_context().dialog_data["len"]:
                dialog_manager.current_context().dialog_data["is_not_last"] = False

            if dialog_manager.current_context().dialog_data["counter"] > 1:
                dialog_manager.current_context().dialog_data["is_not_first"] = True
        case "minus":
            dialog_manager.current_context().dialog_data["counter"] -= 1

            if dialog_manager.current_context().dialog_data["counter"] == 1:
                dialog_manager.current_context().dialog_data["is_not_first"] = False
            if dialog_manager.current_context().dialog_data["counter"] < dialog_manager.current_context().dialog_data[
                "len"]:
                dialog_manager.current_context().dialog_data["is_not_last"] = True
        case "first":
            dialog_manager.current_context().dialog_data["counter"] = 1
            dialog_manager.current_context().dialog_data["is_not_last"] = True
            dialog_manager.current_context().dialog_data["is_not_first"] = False
        case "fin":
            dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data["len"]
            dialog_manager.current_context().dialog_data["is_not_last"] = False
            dialog_manager.current_context().dialog_data["is_not_first"] = True



view_doc_dialog = Dialog(
    Window(
        StaticMedia(
            path="{filename}",
            type=ContentType.PHOTO
        ),
        Row(
            Button(Format("1"),
                   when="is_not_first",
                   id="first",
                   on_click=switch_pages),
            Button(Format("<<"),
                   when="is_not_first",
                   id="minus",
                   on_click=switch_pages),
            Button(Format("{counter}"),
                   id="curr"),
            Button(Format(">>"),
                   id="plus",
                   when="is_not_last",
                   on_click=switch_pages),
            Button(Format("{len}"),
                   id="fin",
                   when="is_not_last",
                   on_click=switch_pages),

        ),
        state=ViewDocSG.choose_action,
        getter=get_data
    ),
    launch_mode=LaunchMode.ROOT
)
