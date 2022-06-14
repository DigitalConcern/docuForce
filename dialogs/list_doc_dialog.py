from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from database import ActiveUsers
from client import get_doc_list
from .view_doc_dialog import ViewDocSG


class ListDocSG(StatesGroup):
    choose_action = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization"))[0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    doc_list = await get_doc_list(access_token, refresh_token, organization)
    text = []
    doc_ids = []
    for doc in doc_list:
        micro_text = f"{doc[1]}{doc[4]} {doc[2]}{doc[0]}"
        text.append(micro_text)
        doc_ids.append(doc[3])

    if len(text) == 0:
        current_doc = "На данный момент у Вас нет документов!"
        return {
            'current_doc': dialog_manager.current_context().dialog_data.get("current_doc", current_doc),
            'is_not_first': False,
            'is_not_last': False,
            'have_documents': False
        }
    else:
        if len(text) <= 1:
            dialog_manager.current_context().dialog_data["is_not_last"] = False

        dialog_manager.current_context().dialog_data["text"] = text
        dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data.get(
            "counter", 0)

        dialog_manager.current_context().dialog_data["current_doc"] = doc_ids[dialog_manager.current_context().dialog_data["counter"]]
        current_doc = text[0]

        return {
            'current_doc': dialog_manager.current_context().dialog_data.get("current_doc", current_doc),
            'is_not_first': dialog_manager.current_context().dialog_data.get("is_not_first", False),
            'is_not_last': dialog_manager.current_context().dialog_data.get("is_not_last", True),
            'have_documents': True
        }


async def switch_pages(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    match button.widget_id:
        case "plus":
            dialog_manager.current_context().dialog_data["counter"] += 1
            dialog_manager.current_context().dialog_data["current_doc"] = \
                dialog_manager.current_context().dialog_data["text"][
                    dialog_manager.current_context().dialog_data["counter"]]

            if dialog_manager.current_context().dialog_data["counter"] + 1 == len(
                    dialog_manager.current_context().dialog_data["text"]):
                dialog_manager.current_context().dialog_data["is_not_last"] = False

            if dialog_manager.current_context().dialog_data["counter"] > 0:
                dialog_manager.current_context().dialog_data["is_not_first"] = True
        case "minus":
            dialog_manager.current_context().dialog_data["counter"] -= 1
            dialog_manager.current_context().dialog_data["current_doc"] = \
                dialog_manager.current_context().dialog_data["text"][
                    dialog_manager.current_context().dialog_data["counter"]]
            if dialog_manager.current_context().dialog_data["counter"] == 0:
                dialog_manager.current_context().dialog_data["is_not_first"] = False
            if dialog_manager.current_context().dialog_data["counter"] < len(
                    dialog_manager.current_context().dialog_data["text"]):
                dialog_manager.current_context().dialog_data["is_not_last"] = True


async def go_to_doc(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await ActiveUsers.filter(user_id=c.from_user.id).update(
        current_document_id=dialog_manager.current_context().dialog_data["current_doc"])
    await dialog_manager.start(ViewDocSG.choose_action)


list_doc_dialog = Dialog(
    Window(
        Format('{current_doc}'),
        Button(
            Format("Просмотр документа"),
            when="have_documents",
            id="doc",
            on_click=go_to_doc
        ),
        Row(

            Button(Format("<<"),
                   when="is_not_first",
                   id="minus",
                   on_click=switch_pages),
            Button(Format(">>"),
                   id="plus",
                   when="is_not_last",
                   on_click=switch_pages),

        ),
        Cancel(Const("⏪ Назад")),
        state=ListDocSG.choose_action,
        getter=get_data
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)
