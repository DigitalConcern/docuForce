from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group, Column
from aiogram_dialog.widgets.text import Const, Format

from client import get_orgs_dict, get_tasks_dict
from database import ActiveUsers
from bot import MyBot


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization"))[0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    tasks_dict = await get_tasks_dict(access_token, refresh_token, organization)
    text = []
    doc_ids = []
    for task in tasks_dict.keys():
        micro_text = f"{tasks_dict[task][1]}✍🏻Тип документа {tasks_dict[task][4]}{tasks_dict[task][2]}{tasks_dict[task][0]}"
        text.append(micro_text)
        doc_ids.append(tasks_dict[task][3])
    if len(text) == 1:
        dialog_manager.current_context().dialog_data["is_first"] = False

    # orgs_list = "Выберите организацию\n\n"
    # for key in orgs_dict.keys():
    #     orgs_list += f'{key}. {orgs_dict[key][0]}\n'
    # dialog_manager.current_context().dialog_data["organization_dict"] = orgs_dict
    # dialog_manager.current_context().dialog_data["organization_list"] = orgs_list
    dialog_manager.current_context().dialog_data["text"] = text
    dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data.get(
        "counter", 0)
    dialog_manager.current_context().dialog_data["current_doc"] = dialog_manager.current_context().dialog_data.get(
        "current_doc", doc_ids[0])
    current_page = text[0]
    return {
        'current_page': dialog_manager.current_context().dialog_data.get("current_page", current_page),
        'is_not_first': dialog_manager.current_context().dialog_data.get("is_not_first", False),
        'is_not_last': dialog_manager.current_context().dialog_data.get("is_not_last", True),
        'text': text,
    }


async def switch_pages(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    match button.widget_id:
        case "plus":
            dialog_manager.current_context().dialog_data["counter"] += 1
            dialog_manager.current_context().dialog_data["current_page"] = \
                dialog_manager.current_context().dialog_data["text"][
                    dialog_manager.current_context().dialog_data["counter"]]

            if dialog_manager.current_context().dialog_data["counter"]+1 == len(
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


async def go_to_doc(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await ActiveUsers.filter(user_id=c.from_user.id).update(
        current_document_id=dialog_manager.current_context().dialog_data["current_doc"])


class TasksSG(StatesGroup):
    choose_action = State()


tasks_dialog = Dialog(Window(
    Format('{current_page}'),
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
    Button(Format("Просмотр документа"),
           id="doc",
           on_click=go_to_doc),
    state=TasksSG.choose_action,
    getter=get_data
),
    launch_mode=LaunchMode.SINGLE_TOP
)
