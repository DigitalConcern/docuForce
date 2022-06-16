from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from .org_dialog import OrgSG


class SettingsSG(StatesGroup):
    change_org = State()
    notifics = State()


settings_dialog = Dialog(
    Window(
        StaticMedia(
            path="resources/sett1.png",
            type=ContentType.PHOTO
        ),
        Start(Const("Сменить организацию"), id="change_org", state=OrgSG.choose_org),
        SwitchTo(Const("Уведомления"), id="notifics", state=SettingsSG.notifics),
        Cancel(Const("⏪ Назад")),
        state=SettingsSG.change_org
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)

