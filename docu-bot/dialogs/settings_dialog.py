import operator

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo, Back, Start, Column, Radio
from aiogram_dialog.widgets.text import Const, Format

from .org_dialog import OrgSG
from database import ActiveUsers
from notifications import loop_notifications_8hrs, loop_notifications_instant, kill_task


class SettingsSG(StatesGroup):
    choose_action = State()
    notifics = State()
    kill = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    radio = dialog_manager.dialog().find("notifications")

    if not radio.is_checked(item_id="0") and not radio.is_checked(item_id="1") and not radio.is_checked(item_id="2"):
        data = (await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("eight_hour_notification", "instant_notification", "not_notification"))[0]

        eight_hour_notification, instant_notification, not_notification = data[0], data[1], data[2]

        if eight_hour_notification:
            await radio.set_checked(item_id="0", event=dialog_manager.event)

        if instant_notification:
            await radio.set_checked(item_id="1", event=dialog_manager.event)

        if not_notification:
            await radio.set_checked(item_id="2", event=dialog_manager.event)

    mode = [
        ("Несколько раз в сутки", "0"),
        ("Обо всех задачах и сообщениях", "1"),
        ("Отключить", "2")
    ]

    return {"mode": mode}


async def state_changed(event: ChatEvent, radio: Radio, manager: DialogManager, item_id: str):
    if item_id == '0':
        await kill_task(event.from_user.id)
        await ActiveUsers.filter(user_id=event.from_user.id).update(eight_hour_notification=True)
        await ActiveUsers.filter(user_id=event.from_user.id).update(instant_notification=False)
        await ActiveUsers.filter(user_id=event.from_user.id).update(not_notification=False)
        await loop_notifications_8hrs(user_id=event.from_user.id, manager=manager)
    if item_id == '1':
        await kill_task(event.from_user.id)
        await ActiveUsers.filter(user_id=event.from_user.id).update(instant_notification=True)
        await ActiveUsers.filter(user_id=event.from_user.id).update(eight_hour_notification=False)
        await ActiveUsers.filter(user_id=event.from_user.id).update(not_notification=False)
        await loop_notifications_instant(user_id=event.from_user.id, manager=manager)
    if item_id == '2':
        await kill_task(event.from_user.id)
        await ActiveUsers.filter(user_id=event.from_user.id).update(instant_notification=False)
        await ActiveUsers.filter(user_id=event.from_user.id).update(eight_hour_notification=False)
        await ActiveUsers.filter(user_id=event.from_user.id).update(not_notification=True)


async def kill_bot(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await kill_task(c.from_user.id)
    await ActiveUsers.filter(user_id=c.from_user.id).delete()
    await dialog_manager.done()


settings_dialog = Dialog(
    Window(Const("Настройки"),
           Start(Const("Сменить организацию 🔄"), id="choose_action", state=OrgSG.choose_org),
           SwitchTo(Const("Уведомления 🔔"), id="notifics", state=SettingsSG.notifics),
           SwitchTo(Const("Выход"), id="killer", state=SettingsSG.kill),
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
                items="mode",
                on_state_changed=state_changed,
            )
        ),
        Back(Const("⏪ Назад")),
        getter=get_data,
        state=SettingsSG.notifics
    ),
    Window(
        Const("Отключить бота?"),
        Row(
            Button(Const("Да ✅"), on_click=kill_bot, id="del"),
            SwitchTo(Const("Нет ❌"), id="backk", state=SettingsSG.choose_action), ),

        getter=get_data,
        state=SettingsSG.kill
    ),

    launch_mode=LaunchMode.ROOT
)
