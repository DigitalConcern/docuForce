from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from bot import DynamicMedia, MyBot
from aiogram_dialog.widgets.text import Const, Format

from database import ActiveUsers
from client import get_doc_list
from .view_doc_dialog import ViewDocSG


class ListDocSG(StatesGroup):
    choose_action = State()
    find = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    wait_msg_id=(await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id,text="Загрузка...")).message_id

    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization"))[0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    dialog_manager.current_context().dialog_data["find_string_doc"] = dialog_manager.current_context().dialog_data.get(
        "find_string_doc", "")

    dialog_manager.current_context().dialog_data["doc_list"] = dialog_manager.current_context().dialog_data.get(
        "doc_list", "")
    if dialog_manager.current_context().dialog_data["doc_list"] == "":
        doc_list = await get_doc_list(access_token=access_token,
                                      refresh_token=refresh_token,
                                      org_id=organization,
                                      contained_string=dialog_manager.current_context().dialog_data["find_string_doc"],
                                      user_id=dialog_manager.event.from_user.id)
        dialog_manager.current_context().dialog_data["doc_list"] = doc_list
    else:
        doc_list = dialog_manager.current_context().dialog_data["doc_list"]
    text = []
    doc_ids = []
    for doc in doc_list:
        micro_text = f"{doc[1]} {doc[4]} {doc[3]} {doc[2]}{doc[0]}{doc[6]}{doc[7]}"
        text.append(micro_text)
        doc_ids.append(doc[5])



    if len(text) == 0:
        await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id, message_id=wait_msg_id)
        if dialog_manager.current_context().dialog_data["find_string_doc"] == "":
            current_doc = "На данный момент у Вас нет документов!"
        else:
            current_doc = f"Документов, которые содержат '{dialog_manager.current_context().dialog_data['find_string_doc']}' не найдено!"
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

        dialog_manager.current_context().dialog_data["current_doc"] = text[
            dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data["current_doc_id"] = doc_ids[
            dialog_manager.current_context().dialog_data["counter"]]
        await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id, message_id=wait_msg_id)

        return {
            'current_doc': dialog_manager.current_context().dialog_data.get("current_doc", "-"),
            'is_not_first': dialog_manager.current_context().dialog_data.get("is_not_first", False),
            'is_not_last': dialog_manager.current_context().dialog_data.get("is_not_last", True),
            'org_id': dialog_manager.current_context().dialog_data.get("org_id", organization),
            'access_token': dialog_manager.current_context().dialog_data.get("access_token", access_token),
            'current_doc_id': dialog_manager.current_context().dialog_data.get("current_doc_id", 0),
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
        current_document_id=dialog_manager.current_context().dialog_data["current_doc_id"])
    dialog_manager.current_context().dialog_data["doc_list"] = ""
    dialog_manager.current_context().dialog_data["counter"] = 0
    dialog_manager.current_context().dialog_data["is_not_first"] = False
    dialog_manager.current_context().dialog_data["is_not_last"] = True
    await dialog_manager.start(ViewDocSG.choose_action)


async def search_handler(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data["find_string_doc"] = m.text
    await dialog_manager.switch_to(ListDocSG.choose_action)


list_doc_dialog = Dialog(
    Window(
        DynamicMedia(
            url="https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{current_doc_id}/page/1",
            url_headers="{access_token}",
            type=ContentType.PHOTO
        ),
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
        getter=get_data,
        parse_mode=ParseMode.HTML
    ),
    Window(
        Const("Введите строку для поиска в документах"),
        MessageInput(search_handler),
        Cancel(Const("⏪ Назад")),
        state=ListDocSG.find,
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)
