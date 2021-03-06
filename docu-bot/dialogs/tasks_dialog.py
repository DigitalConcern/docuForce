import asyncio

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, ParseMode

from aiogram_dialog import Dialog, DialogManager, Window, StartMode, ShowMode
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Format

from client import get_tasks_dict, post_doc_action, post_doc_sign
from database import ActiveUsers, Stats
from bot import MyBot
from dialogs.view_doc_dialog import ViewDocSG


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = list(
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("refresh_token", "access_token",
                                                                                        "organization", "user_org_id",
                                                                                        "new_tasks"))[
        0]
    refresh_token, access_token, organization, user_org_id, curr_tasks = data[0], data[1], data[2], data[3], data[4]

    dialog_manager.current_context().dialog_data["curr_tasks"] = dialog_manager.current_context().dialog_data.get(
        "curr_tasks", curr_tasks)

    dialog_manager.current_context().dialog_data["tasks_dict"] = dialog_manager.current_context().dialog_data.get(
        "tasks_dict", "")
    dialog_manager.current_context().dialog_data["user_org_id"] = user_org_id
    if dialog_manager.current_context().dialog_data["tasks_dict"] == "":
        wait_msg_id = (
            await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text="Загрузка...")).message_id
        tasks_dict = await get_tasks_dict(access_token=access_token,
                                          refresh_token=refresh_token,
                                          org_id=organization,
                                          user_id=dialog_manager.event.from_user.id)
        dialog_manager.current_context().dialog_data["tasks_dict"] = tasks_dict
    else:
        tasks_dict = dialog_manager.current_context().dialog_data["tasks_dict"]
    text = []
    doc_ids = []
    yes_names = []
    task_types = []
    task_ids = []
    doc_att_ids = []
    for task in tasks_dict.keys():
        micro_text = f"{tasks_dict[task][7]}\n<i>{tasks_dict[task][1]}{tasks_dict[task][5]} {tasks_dict[task][4]}{tasks_dict[task][2]}{tasks_dict[task][0]}\n{tasks_dict[task][6]}</i>"
        text.append(micro_text)
        doc_ids.append(tasks_dict[task][3])
        yes_names.append(tasks_dict[task][8])
        task_types.append(tasks_dict[task][9])
        task_ids.append(tasks_dict[task][10])
        doc_att_ids.append(tasks_dict[task][11])
    try:
        await MyBot.bot.delete_message(chat_id=dialog_manager.event.from_user.id, message_id=wait_msg_id)
    except:
        pass

    dialog_manager.current_context().dialog_data["len"] = len(text)

    if dialog_manager.current_context().dialog_data["curr_tasks"] > 0:
        dialog_manager.current_context().dialog_data["len"] = dialog_manager.current_context().dialog_data["curr_tasks"]
        await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).update(new_tasks=0)

    if dialog_manager.current_context().dialog_data["len"] == 0:
        current_page = "На данный момент у Вас нет активных задач!"
        return {
            'current_page': dialog_manager.current_context().dialog_data.get("current_page", current_page),
            'is_not_first': False,
            'is_not_last': False,
            'is_not_one': False,
            'have_tasks': False,
            "no_acq": True,
        }
    else:
        if dialog_manager.current_context().dialog_data["len"] <= 1:
            dialog_manager.current_context().dialog_data["is_not_last"] = False
        if dialog_manager.current_context().dialog_data["len"] == 1:
            dialog_manager.current_context().dialog_data["is_not_one"] = False
        dialog_manager.current_context().dialog_data["text"] = text
        dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data.get(
            "counter", 0)
        dialog_manager.current_context().dialog_data["yes_name"] = dialog_manager.current_context().dialog_data.get(
            "yes_name", "Да")
        dialog_manager.current_context().dialog_data["task_id"] = dialog_manager.current_context().dialog_data.get(
            "task_id", "")
        dialog_manager.current_context().dialog_data["task_id"] = task_ids[
            dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data[
            "task_type_service"] = dialog_manager.current_context().dialog_data.get(
            "task_type_service", "")
        dialog_manager.current_context().dialog_data["task_type_service"] = task_types[
            dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data["yes_name"] = yes_names[
            dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data["current_doc_id"] = doc_ids[
            dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data["doc_att_id"] = doc_att_ids[
            dialog_manager.current_context().dialog_data["counter"]]
        current_page = text[dialog_manager.current_context().dialog_data["counter"]]
        dialog_manager.current_context().dialog_data["current_page"] = current_page
        no_acq = (task_types[dialog_manager.current_context().dialog_data["counter"]] != "ACQUAINTANCE")
        return {
            'current_page': dialog_manager.current_context().dialog_data.get("current_page", current_page),
            'is_not_first': dialog_manager.current_context().dialog_data.get("is_not_first", False),
            'is_not_last': dialog_manager.current_context().dialog_data.get("is_not_last", True),
            'have_tasks': True,
            'user_counter': dialog_manager.current_context().dialog_data.get("counter", 0) + 1,
            'len': dialog_manager.current_context().dialog_data.get("len", 0),
            'is_not_one': dialog_manager.current_context().dialog_data.get("is_not_one", True),
            'yes_name': dialog_manager.current_context().dialog_data.get("yes_name", "Да"),
            "no_acq": no_acq,
        }


async def switch_pages(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    match button.widget_id:
        case "plus":
            dialog_manager.current_context().dialog_data["counter"] += 1
            dialog_manager.current_context().dialog_data["current_page"] = \
                dialog_manager.current_context().dialog_data["text"][
                    dialog_manager.current_context().dialog_data["counter"]]

            if dialog_manager.current_context().dialog_data["counter"] + 1 == \
                    dialog_manager.current_context().dialog_data["len"]:
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
            if dialog_manager.current_context().dialog_data["counter"] < dialog_manager.current_context().dialog_data[
                "len"]:
                dialog_manager.current_context().dialog_data["is_not_last"] = True
        case "first":
            dialog_manager.current_context().dialog_data["counter"] = 0
            dialog_manager.current_context().dialog_data["is_not_last"] = True
            dialog_manager.current_context().dialog_data["is_not_first"] = False
        case "fin":
            dialog_manager.current_context().dialog_data["counter"] = dialog_manager.current_context().dialog_data[
                                                                          "len"] - 1
            dialog_manager.current_context().dialog_data["is_not_last"] = False
            dialog_manager.current_context().dialog_data["is_not_first"] = True


async def go_to_doc(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await ActiveUsers.filter(user_id=c.from_user.id).update(
        current_document_id=dialog_manager.current_context().dialog_data["current_doc_id"])
    dialog_manager.current_context().dialog_data["tasks_dict"] = ""
    dialog_manager.current_context().dialog_data["counter"] = 0
    dialog_manager.current_context().dialog_data["is_not_first"] = False
    dialog_manager.current_context().dialog_data["is_not_last"] = True

    documents = (await Stats.filter(id=0).values_list("documents", flat=True))[0]
    await Stats.filter(id=0).update(documents=documents + 1)

    await dialog_manager.start(ViewDocSG.choose_action)


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
                                    doc_id=dialog_manager.current_context().dialog_data["current_doc_id"],
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

            # msg_mini_text = (await get_task_caption(access_token=access_token, refresh_token=refresh_token,
            #                                         user_id=dialog_manager.event.from_user.id,
            #                                         doc_task_type=dialog_manager.current_context().dialog_data[
            #                                             'task_type_service'], org_id=organization, is_done=True))
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
            msg_text += "🚫"
            data = "DECLINED"
            await post_doc_action(access_token, refresh_token, organization,
                                  dialog_manager.current_context().dialog_data["task_id"], data, c.from_user.id)

            # msg_text += await get_task_caption(access_token=access_token, refresh_token=refresh_token,
            #                                    user_id=dialog_manager.event.from_user.id,
            #                                    doc_task_type=dialog_manager.current_context().dialog_data[
            #                                        'task_type_service'], org_id=organization, is_done=False)
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
    msg_text += f"\n\n"
    msg_text += "<i>" + dialog_manager.current_context().dialog_data["current_page"].partition('<i>')[2]

    await MyBot.bot.send_message(chat_id=dialog_manager.event.from_user.id, text=msg_text, parse_mode=ParseMode.HTML)

    tasks_done = (await Stats.filter(id=0).values_list("tasks_done", flat=True))[0]
    await Stats.filter(id=0).update(tasks_done=tasks_done + 1)

    tasks_amount = \
        (await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).values_list("tasks_amount", flat=True))[0]
    await ActiveUsers.filter(user_id=dialog_manager.event.from_user.id).update(tasks_amount=tasks_amount - 1)

    await dialog_manager.start(TasksSG.choose_action, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)


class TasksSG(StatesGroup):
    choose_action = State()


tasks_dialog = Dialog(
    Window(
        Format('{current_page}'),
        Row(
            Button(Format("{yes_name} ✅"),
                   id="yes",
                   on_click=do_task
                   ),
            Button(Format("Отказать ❌"),
                   id="no",
                   on_click=do_task,
                   when="no_acq"
                   ),
            when="have_tasks"
        ),
        Button(
            Format("Просмотр документа 📄"),
            when="have_tasks",
            id="doc",
            on_click=go_to_doc
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
            Button(Format("{user_counter}"),
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
        # Cancel(Const("Закрыть")),
        state=TasksSG.choose_action,
        getter=get_data,
        parse_mode=ParseMode.HTML
    ),
    launch_mode=LaunchMode.ROOT
)
