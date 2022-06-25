import asyncio

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from bot import MyBot
from database import ActiveUsers, Stats
from .view_doc_dialog import ViewDocSG
from client import get_conversations_dict, post_message_answer, post_doc_action, post_markasread


class MessagesSG(StatesGroup):
    choose_action = State()
    answer = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    # wait_msg_id = (
    #     await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text="Загрузка...")).message_id
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization","new_convs"))[0]
    refresh_token, access_token, organization, curr_convs = data[0], data[1], data[2],data[3]

    dialog_manager.current_context().dialog_data[
        "conversations_dict"] = dialog_manager.current_context().dialog_data.get(
        "conversations_dict", "")
    dialog_manager.current_context().dialog_data[
        "curr_convs"] = dialog_manager.current_context().dialog_data.get(
        "curr_convs", curr_convs)
    if dialog_manager.current_context().dialog_data["conversations_dict"] == "":
        wait_msg_id = (
            await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text="Загрузка...")).message_id
        conversations_dict = await get_conversations_dict(access_token=access_token,
                                                          refresh_token=refresh_token,
                                                          org_id=organization,
                                                          user_id=dialog_manager.event.from_user.id)
        dialog_manager.current_context().dialog_data["conversations_dict"] = conversations_dict
    else:
        conversations_dict = dialog_manager.current_context().dialog_data["conversations_dict"]

    dialog_manager.current_context().dialog_data["len"] = len(conversations_dict)

    text = []
    doc_ids = []
    entity_ids = []
    user_ids = []
    authors_for_resp = []
    for conversation in conversations_dict.keys():
        micro_text = f"{conversations_dict[conversation][1]}" \
                     f"{conversations_dict[conversation][4]}" \
                     f"{conversations_dict[conversation][3]}" \
                     f"{conversations_dict[conversation][2]}" \
                     f"{conversations_dict[conversation][0]}" \
                     f"{conversations_dict[conversation][5]}" \
                     f'\n<i>{conversations_dict[conversation][6]}</i>' \
                     f"\n{conversations_dict[conversation][7]}"
        text.append(micro_text)
        authors_for_resp.append(conversations_dict[conversation][11])
        doc_ids.append(conversations_dict[conversation][10])
        entity_ids.append(conversations_dict[conversation][8])
        user_ids.append(conversations_dict[conversation][9])
    try:
        await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id, message_id=wait_msg_id)
    except:
        pass

    if dialog_manager.current_context().dialog_data["curr_convs"] > 0:
        dialog_manager.current_context().dialog_data["len"] = dialog_manager.current_context().dialog_data["curr_convs"]
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).update(new_convs=0)

    if dialog_manager.current_context().dialog_data["len"] == 0:
        current_page = "На данный момент у Вас нет сообщений!"
        return {
            'current_page': dialog_manager.current_context().dialog_data.get("current_page", current_page),
            'is_not_first': False,
            'is_not_last': False,
            'is_not_one': False,
            'have_tasks': False
        }
    else:
        if dialog_manager.current_context().dialog_data["len"] <= 1:
            dialog_manager.current_context().dialog_data["is_not_last"] = False

        if dialog_manager.current_context().dialog_data["len"] == 1:
            dialog_manager.current_context().dialog_data["is_not_one"] = False

        dialog_manager.current_context().dialog_data["text"] = text
        dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data.get(
            "counter", 0)

        dialog_manager.current_context().dialog_data["current_user"] = user_ids[
            dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data["current_doc"] = doc_ids[
            dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data["current_task"] = entity_ids[
            dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data["current_author_for_resp"] = authors_for_resp[
            dialog_manager.current_context().dialog_data["counter"]]
        current_page = text[0]

        return {
            'current_page': dialog_manager.current_context().dialog_data.get("current_page", current_page),
            'is_not_first': dialog_manager.current_context().dialog_data.get("is_not_first", False),
            'is_not_last': dialog_manager.current_context().dialog_data.get("is_not_last", True),
            'len': dialog_manager.current_context().dialog_data.get("len", 0),
            'is_not_one': dialog_manager.current_context().dialog_data.get("is_not_one", True),
            'user_counter': dialog_manager.current_context().dialog_data.get("counter", 0) + 1,
            'have_tasks': True
        }


async def switch_pages(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    match button.widget_id:
        case "plus":
            dialog_manager.current_context().dialog_data["counter"] += 1
            dialog_manager.current_context().dialog_data["current_page"] = \
                dialog_manager.current_context().dialog_data["text"][
                    dialog_manager.current_context().dialog_data["counter"]]

            if dialog_manager.current_context().dialog_data["counter"] + 1 == len(
                    dialog_manager.current_context().dialog_data["text"]):
                dialog_manager.current_context().dialog_data["is_not_last"] = False

            if dialog_manager.current_context().dialog_data["counter"] > 0:
                dialog_manager.current_context().dialog_data["is_not_first"] = True
        case "minus":
            dialog_manager.current_context().dialog_data["counter"] -= 1
            dialog_manager.current_context().dialog_data["current_page"] = \
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


async def answer_message(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization"))[0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    await post_message_answer(refresh_token=refresh_token,
                              access_token=access_token,
                              org_id=organization,
                              entity_id=dialog_manager.current_context().dialog_data["current_doc"],
                              user_oguid=dialog_manager.current_context().dialog_data["current_user"],
                              answer=m.text,
                              user_id=m.from_user.id,
                              task_id=dialog_manager.current_context().dialog_data["current_task"])
    dialog_manager.current_context().dialog_data["conversations_dict"] = ""

    await post_markasread(
        access_token=access_token,
        refresh_token=refresh_token,
        org_id=organization, task_id=dialog_manager.current_context().dialog_data["current_task"],
        user_id=m.from_user.id)

    await MyBot.bot.send_message(m.from_user.id,
                                 f"Сообщение:\n<i>{m.text}</i>\nДля пользователя {dialog_manager.current_context().dialog_data['current_author_for_resp']}\nОтправлено!", parse_mode=ParseMode.HTML)

    messages_done = (await Stats.all().values_list("messages_done", flat=True))[0]
    await Stats.all().update(messages_done=messages_done + 1)

    await dialog_manager.done()

    await asyncio.sleep(1)

    await dialog_manager.start(MessagesSG.choose_action)


async def close_msg(m: Message, dialog: Dialog, dialog_manager: DialogManager):
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization"))[0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    await post_doc_action(refresh_token=refresh_token,
                          access_token=access_token,
                          org_id=organization,
                          action="SOLVED",
                          task_id=dialog_manager.current_context().dialog_data["current_task"],
                          user_id=m.from_user.id)
    dialog_manager.current_context().dialog_data["conversations_dict"] = ""

    await MyBot.bot.send_message(m.from_user.id,
                                 f"Диалог с пользователем {dialog_manager.current_context().dialog_data['current_author_for_resp']}\nЗавершен!")

    messages_done = (await Stats.all().values_list("messages_done", flat=True))[0]
    await Stats.all().update(messages_done=messages_done + 1)

    await dialog_manager.done()

    await asyncio.sleep(1)

    await dialog_manager.start(MessagesSG.choose_action)


async def go_to_doc(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await ActiveUsers.filter(user_id=c.from_user.id).update(
        current_document_id=dialog_manager.current_context().dialog_data["current_doc"])
    dialog_manager.current_context().dialog_data["conversations_dict"] = ""

    documents = (await ActiveUsers.all().values_list("documents", flat=True))[0]
    await ActiveUsers.all().update(documents=documents + 1)

    await dialog_manager.start(ViewDocSG.choose_action)


messages_dialog = Dialog(
    Window(
        Format('{current_page}'),
        Row(
            SwitchTo(Format("Ответить 📝️"),
                     when="have_tasks",
                     id="answer",
                     state=MessagesSG.answer
                     ),
            Button(Format("Закрыть ❌"),
                   when="have_tasks",
                   id="doc",
                   on_click=close_msg),
        ),
        Button(
            Format("Просмотр документа 📄"),
            when="have_tasks",
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
        # Cancel(Const("⏪ Назад")),
        state=MessagesSG.choose_action,
        getter=get_data,
        parse_mode=ParseMode.HTML
    ),
    Window(
        Const("Введите текст ответа"),
        MessageInput(answer_message),
        state=MessagesSG.answer
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)
