from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from bot import MyBot
from .tasks_dialog import TasksSG
# from .search_dialog import SearchSG
from .list_doc_dialog import ListDocSG
from .settings_dialog import SettingsSG
from .messages_dialog import MessagesSG


class MenuSG(StatesGroup):
    choose_action = State()


menu_dialog = Dialog(
    Window(
        StaticMedia(
             path="resources/logo.png",
             type=ContentType.PHOTO
        ),
        Start(Const("Мои задачи"), id="tasks", state=TasksSG.choose_action),
        Start(Const("Поиск документа"), id="search", state=ListDocSG.find),
        Start(Const("Список документов"), id="list", state=ListDocSG.choose_action),
        Start(Const("Настройки"), id="settings", state=SettingsSG.change_org),
        Start(Const("Сообщения"), id="messages", state=MessagesSG.choose_action),
        state=MenuSG.choose_action
    ),
    launch_mode=LaunchMode.ROOT
)
