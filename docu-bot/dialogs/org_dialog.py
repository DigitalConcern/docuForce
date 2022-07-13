from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode, CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.kbd import Select, Group
from aiogram_dialog.widgets.text import Format

from bot import MyBot
from client import get_orgs_dict
from database import ActiveUsers
from metadata import Metadata
from notifications import kill_task, start_notifications


class OrgSG(StatesGroup):
    choose_org = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    wait_msg_id = (
        await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text="Загрузка...")).message_id
    data = list(await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token",
                                                                                                "access_token"))[0]
    refresh_token, access_token = data[0], data[1]

    orgs_dict = await get_orgs_dict(access_token=access_token,
                                    refresh_token=refresh_token,
                                    user_id=dialog_manager.event.from_user.id)
    orgs_list = "Выберите организацию\n\n"
    for key in orgs_dict.keys():
        orgs_list += f'{key}. {orgs_dict[key][0]}\n'
    dialog_manager.current_context().dialog_data["organization_dict"] = orgs_dict

    await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id, message_id=wait_msg_id)

    return {
        'organization_keys': orgs_dict.keys(),
        'organization_list': dialog_manager.current_context().dialog_data.get("organization_list", orgs_list)
    }


async def on_org_clicked(c: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    org_uuid = dialog_manager.current_context().dialog_data["organization_dict"][item_id][1]
    org_name = dialog_manager.current_context().dialog_data["organization_dict"][item_id][0]

    await ActiveUsers.filter(user_id=c.from_user.id).update(organization=org_uuid)

    access_token = (await ActiveUsers.filter(user_id=c.from_user.id).values_list("access_token", flat=True))[0]
    await Metadata.update_meta(user_id=c.from_user.id, access_token=access_token)

    await MyBot.bot.send_message(c.from_user.id, f"Организация\n{org_name}\nуспешно выбрана!")
    await MyBot.bot.send_message(c.from_user.id, f"Теперь Вы можете использовать любую команду из меню!")

    await dialog_manager.reset_stack(remove_keyboard=True)
    await kill_task(c.from_user.id)
    await start_notifications(user_id=c.from_user.id, manager=dialog_manager.bg())


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
        # Cancel(Const("⏪ Назад")),
        state=OrgSG.choose_org,
        getter=get_data,
        parse_mode=ParseMode.HTML
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)
