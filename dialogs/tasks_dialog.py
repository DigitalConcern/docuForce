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
    text=[]
    for task in tasks_dict.keys():
        micro_text=f"{tasks_dict[task][1]}✍🏻Тип документа{tasks_dict[task][4]}{tasks_dict[task][2]}{tasks_dict[task][0]}"
        text.append(micro_text)
    # orgs_list = "Выберите организацию\n\n"
    # for key in orgs_dict.keys():
    #     orgs_list += f'{key}. {orgs_dict[key][0]}\n'
    # dialog_manager.current_context().dialog_data["organization_dict"] = orgs_dict
    # dialog_manager.current_context().dialog_data["organization_list"] = orgs_list
    dialog_manager.current_context().dialog_data.get("current_page", 0)
    return {
        # 'organization_keys': orgs_dict.keys(),
        'current_page': dialog_manager.current_context().dialog_data.get("current_page", 0),
        'text': text,
    }


class TasksSG(StatesGroup):
    choose_action = State()


tasks_dialog = Dialog(Window(
    Format('{text}'),
    state=TasksSG.choose_action,
    getter=get_data
),
    launch_mode=LaunchMode.SINGLE_TOP
)

