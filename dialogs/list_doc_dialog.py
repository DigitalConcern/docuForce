import asyncio

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from bot import DynamicMedia, MyBot
from aiogram_dialog.widgets.text import Const, Format

from database import ActiveUsers, Stats
from client import get_doc_list
from .view_doc_dialog import ViewDocSG


class ListDocSG(StatesGroup):
    choose_action = State()
    find = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    wait_msg_id = (
        await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text="Загрузка...")).message_id

    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization"))[0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    dialog_manager.current_context().dialog_data["find_string_doc"] = dialog_manager.current_context().dialog_data.get(
        "find_string_doc", "")

    dialog_manager.current_context().dialog_data["doc_list"] = dialog_manager.current_context().dialog_data.get(
        "doc_list", "")
    if dialog_manager.current_context().dialog_data["doc_list"] == "":
        while dialog_manager.current_context().dialog_data["doc_list"] == "":
            try:
                doc_list = await get_doc_list(access_token=access_token,
                                              refresh_token=refresh_token,
                                              org_id=organization,
                                              contained_string=dialog_manager.current_context().dialog_data["find_string_doc"],
                                              user_id=dialog_manager.event.from_user.id)
            except:
                pass
            await asyncio.sleep(0.5)
            dialog_manager.current_context().dialog_data["doc_list"] = doc_list
    else:
        doc_list = dialog_manager.current_context().dialog_data["doc_list"]
    text = []
    doc_ids = []
    for doc in doc_list:
        micro_text = f"{doc[7]}<i>{doc[1]}{doc[4]} {doc[3]} {doc[2]}{doc[0]}{doc[6]}</i>"
        text.append(micro_text)
        doc_ids.append(doc[5])

    dialog_manager.current_context().dialog_data["len"] = len(text)
    if dialog_manager.current_context().dialog_data["len"] == 0:
        await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id, message_id=wait_msg_id)
        if dialog_manager.current_context().dialog_data["find_string_doc"] == "":
            current_doc = "На данный момент у Вас нет документов!"
            dialog_manager.current_context().dialog_data["current_doc"] = "На данный момент у Вас нет документов!"
        else:
            current_doc = f"Документов, которые содержат '{dialog_manager.current_context().dialog_data['find_string_doc']}' не найдено!"
            dialog_manager.current_context().dialog_data[
                "current_doc"] = f"Документов, которые содержат '{dialog_manager.current_context().dialog_data['find_string_doc']}' не найдено!"
        return {
            'current_doc': dialog_manager.current_context().dialog_data.get("current_doc", current_doc),
            'is_not_first': False,
            'is_not_last': False,
            'is_not_one': False,
            'have_documents': False,
            'org_id': dialog_manager.current_context().dialog_data.get("org_id", organization),
            'current_doc_id': dialog_manager.current_context().dialog_data.get("current_doc_id", 0),
            'access_token': dialog_manager.current_context().dialog_data.get("access_token", access_token),

        }
    else:
        if len(text) == 1:
            dialog_manager.current_context().dialog_data["is_not_last"] = False
            dialog_manager.current_context().dialog_data["is_not_one"] = False

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
            'have_documents': True,
            'counter': dialog_manager.current_context().dialog_data.get("counter", 0),
            'user_counter': dialog_manager.current_context().dialog_data.get("counter", 0) + 1,
            'len': dialog_manager.current_context().dialog_data.get("len", len(text)),
            'is_not_one': dialog_manager.current_context().dialog_data.get("is_not_one", True),
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
        case "first":
            dialog_manager.current_context().dialog_data["counter"] = 0
            dialog_manager.current_context().dialog_data["is_not_last"] = True
            dialog_manager.current_context().dialog_data["is_not_first"] = False
        case "fin":
            dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data[
                                                                          "len"] - 1
            dialog_manager.current_context().dialog_data["is_not_last"] = False
            dialog_manager.current_context().dialog_data["is_not_first"] = True


async def go_to_doc(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await ActiveUsers.filter(user_id=c.from_user.id).update(
        current_document_id=dialog_manager.current_context().dialog_data["current_doc_id"])
    dialog_manager.current_context().dialog_data["doc_list"] = ""
    dialog_manager.current_context().dialog_data["counter"] = 0
    dialog_manager.current_context().dialog_data["is_not_first"] = False
    dialog_manager.current_context().dialog_data["is_not_last"] = True

    documents = (await Stats.filter(id=0).values_list("documents", flat=True))[0]
    await Stats.filter(id=0).update(documents=documents + 1)

    await dialog_manager.start(ViewDocSG.choose_action)


async def search_handler(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data["find_string_doc"] = m.text
    await dialog_manager.switch_to(ListDocSG.choose_action)


list_doc_dialog = Dialog(
    Window(
        DynamicMedia(
            url="https://im-api.df-backend-dev.dev.info-logistics.eu/orgs/{org_id}/documents/{current_doc_id}/page/1",
            url_headers="{access_token}",
            when='have_documents',
            type=ContentType.PHOTO
        ),
        Format('{current_doc}'),
        Button(
            Format("Просмотр документа 📄"),
            when="have_documents",
            id="doc",
            on_click=go_to_doc
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
            Button(Format("{user_counter}"),
                   when="is_not_one",
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

        # Cancel(Const("Закрыть")),
        state=ListDocSG.choose_action,
        getter=get_data,
        parse_mode=ParseMode.HTML
    ),
    Window(
        Const("Введите строку для поиска в документах 🔍"),
        MessageInput(search_handler),
        # Cancel(Const("⏪ Назад")),
        state=ListDocSG.find,
    ),
    launch_mode=LaunchMode.ROOT
)
