from io import BytesIO

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, ParseMode, ContentType, InputFile

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.kbd import Button, Row, Cancel
from aiogram_dialog.widgets.text import Const, Format

from bot import MyBot, DynamicMedia
from client import get_doc_dict, post_doc_action, post_doc_sign, get_file
from database import ActiveUsers, Stats


class ViewDocSG(StatesGroup):
    choose_action = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    wait_msg_id = (
        await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text="Загрузка...")).message_id
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "current_document_id",
                                                                                        "organization", "user_org_id",
                                                                                        "current_document_id"))[0]
    refresh_token, access_token, current_document_id, organization, user_org_id, current_document_id = data[0], data[1], \
                                                                                                       data[2], data[3], \
                                                                                                       data[4], data[5]

    dialog_manager.current_context().dialog_data["user_org_id"] = user_org_id
    dialog_manager.current_context().dialog_data["org_id"] = organization
    dialog_manager.current_context().dialog_data["current_document_id"] = current_document_id
    dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data.get(
        "counter", 1)
    dialog_manager.current_context().dialog_data["access_token"] = access_token

    doc = await get_doc_dict(access_token=access_token,
                             refresh_token=refresh_token,
                             org_id=organization,
                             doc_id=current_document_id,
                             page=dialog_manager.current_context().dialog_data["counter"],
                             user_id=dialog_manager.event.from_user.id)

    dialog_manager.current_context().dialog_data["len"] = int(doc["len"])
    dialog_manager.current_context().dialog_data["doc_att_id"] = doc["doc_att_id"]
    if dialog_manager.current_context().dialog_data["len"] <= 1:
        dialog_manager.current_context().dialog_data["is_not_last"] = False

    dialog_manager.current_context().dialog_data["is_task"] = dialog_manager.current_context().dialog_data.get(
        "is_task", False)
    dialog_manager.current_context().dialog_data["yes_name"] = dialog_manager.current_context().dialog_data.get(
        "yes_name", "Да")
    dialog_manager.current_context().dialog_data["task_id"] = dialog_manager.current_context().dialog_data.get(
        "task_id", "")
    dialog_manager.current_context().dialog_data["text"] = doc["text"]
    if doc["task_id"] != "":
        dialog_manager.current_context().dialog_data["is_task"] = True
        dialog_manager.current_context().dialog_data["yes_name"] = doc["task_type"]
        dialog_manager.current_context().dialog_data["task_id"] = doc["task_id"]
        dialog_manager.current_context().dialog_data["task_type_service"] = doc["task_type_service"]

    await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id, message_id=wait_msg_id)




    return {
        'is_not_first': dialog_manager.current_context().dialog_data.get("is_not_first", False),
        'is_not_last': dialog_manager.current_context().dialog_data.get("is_not_last", True),
        'len': dialog_manager.current_context().dialog_data["len"],
        'is_not_one': dialog_manager.current_context().dialog_data["len"] > 1,
        'counter': dialog_manager.current_context().dialog_data["counter"],
        'is_task': dialog_manager.current_context().dialog_data.get("is_task", False),
        'yes_name': dialog_manager.current_context().dialog_data.get("yes_name", "Да"),
        'org_id': dialog_manager.current_context().dialog_data.get("org_id", ""),
        'access_token': dialog_manager.current_context().dialog_data.get("access_token", ""),
        'current_document_id': dialog_manager.current_context().dialog_data.get("current_document_id", ""),
        'doc_att_id': dialog_manager.current_context().dialog_data.get("doc_att_id", ""),
    }


async def switch_pages(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    match button.widget_id:
        case "plus":
            dialog_manager.current_context().dialog_data["counter"] += 1
            if dialog_manager.current_context().dialog_data["counter"] == \
                    dialog_manager.current_context().dialog_data["len"]:
                dialog_manager.current_context().dialog_data["is_not_last"] = False

            if dialog_manager.current_context().dialog_data["counter"] > 1:
                dialog_manager.current_context().dialog_data["is_not_first"] = True
        case "minus":
            dialog_manager.current_context().dialog_data["counter"] -= 1

            if dialog_manager.current_context().dialog_data["counter"] == 1:
                dialog_manager.current_context().dialog_data["is_not_first"] = False
            if dialog_manager.current_context().dialog_data["counter"] < dialog_manager.current_context().dialog_data[
                "len"]:
                dialog_manager.current_context().dialog_data["is_not_last"] = True
        case "first":
            dialog_manager.current_context().dialog_data["counter"] = 1
            dialog_manager.current_context().dialog_data["is_not_last"] = True
            dialog_manager.current_context().dialog_data["is_not_first"] = False
        case "fin":
            dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data[
                "len"]
            dialog_manager.current_context().dialog_data["is_not_last"] = False
            dialog_manager.current_context().dialog_data["is_not_first"] = True


async def do_task(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization"))[0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    msg_text = ""
    match button.widget_id:
        case "yes":
            data = "SOLVED"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "SIGNING":
                await post_doc_sign(access_token=access_token,
                                    refresh_token=refresh_token,
                                    org_id=organization,
                                    user_oguid=dialog_manager.current_context().dialog_data["user_org_id"],
                                    att_doc_id=dialog_manager.current_context().dialog_data["doc_att_id"],
                                    doc_id=dialog_manager.current_context().dialog_data["current_document_id"],
                                    user_id=dialog_manager.event.from_user.id)
                msg_text += "🖋 "
            else:
                await post_doc_action(access_token=access_token,
                                      refresh_token=refresh_token,
                                      org_id=organization,
                                      task_id=dialog_manager.current_context().dialog_data["task_id"],
                                      action=data,
                                      user_id=c.from_user.id)
                msg_text += "🆗 "

            # msg_text += await get_task_caption(access_token=access_token, refresh_token=refresh_token,
            #                                    user_id=dialog_manager.event.from_user.id,
            #                                    doc_task_type=dialog_manager.current_context().dialog_data[
            #                                        'task_type_service'], org_id=organization, is_done=True)
            if dialog_manager.current_context().dialog_data["task_type_service"] == "APPROVAL":
                msg_text += "Вы согласовали документ"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "SIGNING":
                msg_text += "Вы подписали документ"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "INSPECTION":
                msg_text += "Вы проинспектировали документ"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "ACQUAINTANCE":
                msg_text += "Вы ознакомились с документом"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "PROCESSING":
                msg_text += "Вы обработали документ"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "CONFIRMATION":
                msg_text += "Вы утвердили документ"
        case "no":
            data = "DECLINED"
            msg_text += "🚫"
            await post_doc_action(access_token, refresh_token, organization,
                                  dialog_manager.current_context().dialog_data["task_id"], data, c.from_user.id)
            if dialog_manager.current_context().dialog_data["task_type_service"] == "APPROVAL":
                msg_text += "Вы отказали в согласовании документа"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "SIGNING":
                msg_text += "Вы отказали в подписи документа"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "INSPECTION":
                msg_text += "Вы отказали в инспектировании документа"
            # if dialog_manager.current_context().dialog_data["task_type_service"] == "ACQUAINTANCE":
            #     msg_text += "Вы ознакомились с документом"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "PROCESSING":
                msg_text += "Вы отказали в обработке"
            if dialog_manager.current_context().dialog_data["task_type_service"] == "CONFIRMATION":
                msg_text += "Вы отказали в утверждении"

    msg_text += "\n<i>" + dialog_manager.current_context().dialog_data["text"] + "</i>"
    await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text=msg_text,parse_mode=ParseMode.HTML)

    command_tasks = (await Stats.filter(id=0).values_list("command_tasks", flat=True))[0]
    await Stats.filter(id=0).update(command_tasks=command_tasks + 1)

    tasks_amount = (await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("tasks_amount", flat=True))[0]
    await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).update(tasks_amount=tasks_amount - 1)

    await dialog_manager.reset_stack(remove_keyboard=True)


async def download_file(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "current_document_id",
                                                                                        "organization"))[0]
    refresh_token, access_token, current_document_id, organization = data[0], data[1], data[2], data[3]
    file_text = await get_file(access_token=access_token, refresh_token=refresh_token, org_id=organization,
                               doc_att_id=dialog_manager.current_context().dialog_data["doc_att_id"],
                               user_id=c.from_user.id)
    file = InputFile(filename=file_text["file_title"], path_or_bytesio=BytesIO(file_text["file_content_bytes"]))
    await MyBot.bot.send_document(chat_id=c.from_user.id, document=file)


view_doc_dialog = Dialog(
    Window(
        DynamicMedia(
            url="https://api.docuforce.infologistics.ru/orgs/{org_id}/documents/{"
                "current_document_id}/page/{counter}",
            url_headers="{access_token}",
            type=ContentType.PHOTO
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
            Button(Format("{counter}"),
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
        Button(Const("Скачать 📥"),
               on_click=download_file,
               id="download"),
        Row(
            Button(Format("{yes_name} ✅"),
                   when="is_task",
                   id="yes",
                   on_click=do_task),
            Button(Format("Отказать ❌"),
                   when="is_task",
                   id="no",
                   on_click=do_task),

        ),
        Cancel(Const("⏪ Назад")),
        state=ViewDocSG.choose_action,
        getter=get_data
    ),

    launch_mode=LaunchMode.SINGLE_TOP
)
