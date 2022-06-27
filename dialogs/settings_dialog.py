import asyncio
import operator
from asyncio import CancelledError

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group, Checkbox, \
    ManagedCheckboxAdapter, Column, Radio
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from bot import MyBot
from .org_dialog import OrgSG
from database import ActiveUsers
from notifications import loop_notifications_8hrs, loop_notifications_instant, kill_task


class SettingsSG(StatesGroup):
    choose_action = State()
    notifics = State()
    kill = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    # wait_msg_id = (
    #     await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text="Загрузка...")).message_id
    radio = dialog_manager.dialog().find("notifications")
    #
    # await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id, message_id=wait_msg_id)

    if not radio.is_checked(item_id="0") and not radio.is_checked(item_id="1"):
        if (await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("eight_hour_notification",
                                                                                            flat=True))[0]:
            await radio.set_checked(item_id="0", event=dialog_manager.event)

        if (await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("instant_notification",
                                                                                            flat=True))[0]:
            await radio.set_checked(item_id="1", event=dialog_manager.event)


async def state_changed(event: ChatEvent, radio: Radio, manager: DialogManager, item_id: str):
    if item_id == '0':
        try:
            for task in asyncio.all_tasks():
                if task.get_name() == str(event.from_user.id):
                    task.cancel()
        except CancelledError:
            pass
        await ActiveUsers.filter(user_id=event.from_user.id).update(eight_hour_notification=True)
        await ActiveUsers.filter(user_id=event.from_user.id).update(instant_notification=False)
        await loop_notifications_8hrs(user_id=event.from_user.id, manager=manager)
    if item_id == '1':
        try:
            for task in asyncio.all_tasks():
                if task.get_name() == str(event.from_user.id):
                    task.cancel()
        except CancelledError:
            pass
        await ActiveUsers.filter(user_id=event.from_user.id).update(instant_notification=True)
        await ActiveUsers.filter(user_id=event.from_user.id).update(eight_hour_notification=False)
        await loop_notifications_instant(user_id=event.from_user.id, manager=manager)


async def kill_bot(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await kill_task(c.from_user.id)
    await ActiveUsers.filter(user_id=c.from_user.id).delete()
    await dialog_manager.done()


settings_dialog = Dialog(
    Window(
        Start(Const("Сменить организацию 🔄"), id="choose_action", state=OrgSG.choose_org),
        SwitchTo(Const("Уведомления 🔔"), id="notifics", state=SettingsSG.notifics),
        SwitchTo(Const("Уведомления 🔔"), id="killer", state=SettingsSG.kill),
        state=SettingsSG.choose_action
    ),
    Window(
        Const("Выберите удобный для Вас режим уведомлений 🔔"),
        Column(
            Radio(
                Format("🔘 {item[0]}"),
                Format("⚪️ {item[0]}"),
                id="notifications",
                item_id_getter=operator.itemgetter(1),
                items=[
                    ("Несколько раз в сутки", 0),
                    ("Обо всех задачах и сообщениях", 1)
                ],
                on_state_changed=state_changed,
            )
        ),
        Back(Const("⏪ Назад")),
        getter=get_data,
        state=SettingsSG.notifics
    ),
    Window(
        Const("Отключить бота?"),
        Row(Button(
            Const("Да ✅"), on_click=kill_bot, id="del"
        ),
            Back(Const("Нет ❌")), ),

        getter=get_data,
        state=SettingsSG.kill
    ),

    launch_mode=LaunchMode.SINGLE_TOP
)
