from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from client import get_doc_dict
from database import ActiveUsers


class ViewDocSG(StatesGroup):
    choose_action = State()



async def get_data(dialog_manager: DialogManager, **kwargs):
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "current_document_id",
                                                                                        "organization"))[0]
    refresh_token, access_token, current_document_id, organization = data[0], data[1], data[2], data[3]

    doc_bytes = await get_doc_dict(access_token, refresh_token, organization, current_document_id, 1)
    import base64
    imgdata = base64.b64decode(doc_bytes)
    filename = f'{current_document_id}.jpg'
    with open(filename, 'wb') as f:
        f.write(imgdata)
    f.close()

    return {
        'filename': filename
    }


view_doc_dialog = Dialog(
    Window(
        StaticMedia(
            path="{filename}",
            type=ContentType.PHOTO
        ),
        state=ViewDocSG.choose_action,
        getter=get_data
    ),
    launch_mode=LaunchMode.ROOT
)
