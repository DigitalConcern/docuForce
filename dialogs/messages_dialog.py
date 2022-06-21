from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from bot import MyBot
from database import ActiveUsers
from .view_doc_dialog import ViewDocSG
from client import get_conversations_dict, post_message_answer


class MessagesSG(StatesGroup):
    choose_action = State()
    answer = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    # wait_msg_id = (
    #     await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text="Загрузка...")).message_id
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization"))[0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    dialog_manager.current_context().dialog_data["conversations_dict"] = dialog_manager.current_context().dialog_data.get(
        "conversations_dict", "")

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

    text = []
    doc_ids = []
    entity_ids = []
    user_ids = []
    for conversation in conversations_dict.keys():
        micro_text = f"{conversations_dict[conversation][1]}" \
                     f"{conversations_dict[conversation][4]}" \
                     f"{conversations_dict[conversation][3]}" \
                     f"{conversations_dict[conversation][2]}" \
                     f"{conversations_dict[conversation][0]}" \
                     f"{conversations_dict[conversation][5]}" \
                     f'<i>{"".join(reversed(conversations_dict[conversation][6]))}</i>' \
                     f"\n{conversations_dict[conversation][7]}"
        text.append(micro_text)
        doc_ids.append(conversation)
        entity_ids.append(conversations_dict[conversation][8])
        user_ids.append(conversations_dict[conversation][9])
    try:
        await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id, message_id=wait_msg_id)
    except:
        pass
    if len(text) == 0:
        current_page = "На данный момент у Вас нет сообщений!"
        return {
            'current_page': dialog_manager.current_context().dialog_data.get("current_page", current_page),
            'is_not_first': False,
            'is_not_last': False,
            'have_tasks': False
        }
    else:
        if len(text) <= 1:
            dialog_manager.current_context().dialog_data["is_not_last"] = False

        dialog_manager.current_context().dialog_data["text"] = text
        dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data.get(
            "counter", 0)

        dialog_manager.current_context().dialog_data["current_user"] = user_ids[dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data["current_doc"] = doc_ids[dialog_manager.current_context().dialog_data["counter"]]
        current_page = text[0]

        return {
            'current_page': dialog_manager.current_context().dialog_data.get("current_page", current_page),
            'is_not_first': dialog_manager.current_context().dialog_data.get("is_not_first", False),
            'is_not_last': dialog_manager.current_context().dialog_data.get("is_not_last", True),
            'have_tasks': True
        }


async def switch_pages(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    match button.widget_id:
        case "plus":
            dialog_manager.current_context().dialog_data["counter"] += 1
            dialog_manager.current_context().dialog_data["current_page"] = \
                dialog_manager.current_context().dialog_data["text"][
                    dialog_manager.current_context().dialog_data["counter"]]

            if dialog_manager.current_context().dialog_data["counter"] +1 == len(
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
                              user_id=m.from_user.id)
    dialog_manager.current_context().dialog_data["conversations_dict"] = ""

    await dialog_manager.switch_to(MessagesSG.choose_action)


async def go_to_doc(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await ActiveUsers.filter(user_id=c.from_user.id).update(
        current_document_id=dialog_manager.current_context().dialog_data["current_doc"])
    dialog_manager.current_context().dialog_data["conversations_dict"] = ""
    await dialog_manager.start(ViewDocSG.choose_action)


messages_dialog = Dialog(
    Window(
        Format('{current_page}'),
        SwitchTo(Format("Ответить"),
                 id="answer",
                 state=MessagesSG.answer
                 ),
        Button(
            Format("Просмотр документа"),
            when="have_tasks",
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
