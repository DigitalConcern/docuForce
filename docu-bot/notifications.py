import asyncio
from asyncio import CancelledError
from collections import defaultdict

from aiogram.types import ParseMode
from aiogram_dialog import StartMode, BaseDialogManager

from bot import MyBot
from client import get_tasks_dict, get_conversations_dict, get_tasks_amount, get_conversations_amount
from database import ActiveUsers

from dialogs.tasks_dialog import TasksSG
from dialogs.messages_dialog import MessagesSG


async def msg_8hrs(user_id: int, manager: BaseDialogManager):
    counter = 0
    data = \
        (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token",
                                                               "organization"))[
            0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    conversations_amount = await get_conversations_amount(user_id=user_id,
                                                          refresh_token=refresh_token,
                                                          access_token=access_token,
                                                          org_id=organization)

    tasks_amount = await get_tasks_amount(user_id=user_id,
                                          refresh_token=refresh_token,
                                          access_token=access_token,
                                          org_id=organization)

    await ActiveUsers.filter(user_id=user_id).update(conversations_amount=conversations_amount,
                                                     tasks_amount=tasks_amount)

    try:
        while True:
            data = \
                (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token",
                                                                       "organization"))[
                    0]
            refresh_token, access_token, organization = data[0], data[1], data[2]

            conversations_amount = \
                (await ActiveUsers.filter(user_id=user_id).values_list("conversations_amount", flat=True))[0]

            tasks_amount = (await ActiveUsers.filter(user_id=user_id).values_list("tasks_amount", flat=True))[0]

            new_tasks_amount = await get_tasks_amount(user_id=user_id,
                                                      refresh_token=refresh_token,
                                                      access_token=access_token,
                                                      org_id=organization)

            new_convers_amount = await get_conversations_amount(user_id=user_id,
                                                                refresh_token=refresh_token,
                                                                access_token=access_token,
                                                                org_id=organization)

            diff_msgs_in_conv = new_convers_amount - conversations_amount

            counter += 1
            if counter >= 96:
                if diff_msgs_in_conv > 0:
                    if [11, 12, 13, 14].__contains__(diff_msgs_in_conv):
                        await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщений!")
                    else:
                        match diff_msgs_in_conv % 10:
                            case 1:
                                await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новое сообщение!")
                            case 2 | 3 | 4:
                                await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщения!")
                            case _:
                                await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщений!")

                    await ActiveUsers.filter(user_id=user_id).update(new_convs=diff_msgs_in_conv)
                    await ActiveUsers.filter(user_id=user_id).update(conversations_amount=new_convers_amount)
                    await manager.start(MessagesSG.choose_action, mode=StartMode.RESET_STACK)

                await asyncio.sleep(2)

                diff_tasks = new_tasks_amount - tasks_amount

                if diff_tasks > 0:
                    if [11, 12, 13, 14].__contains__(diff_tasks):
                        await MyBot.bot.send_message(user_id, f"У Вас {diff_tasks} новых задач!")
                    else:
                        match diff_tasks % 10:
                            case 1:
                                await MyBot.bot.send_message(user_id, f"У Вас {diff_tasks} новая задача!")
                            case 2 | 3 | 4:
                                await MyBot.bot.send_message(user_id, f"У Вас {diff_tasks} новые задачи!")
                            case _:
                                await MyBot.bot.send_message(user_id, f"У Вас {diff_tasks} новых задач!")

                    await ActiveUsers.filter(user_id=user_id).update(tasks_amount=new_tasks_amount)
                    await ActiveUsers.filter(user_id=user_id).update(new_tasks=diff_tasks)
                    await manager.start(TasksSG.choose_action, mode=StartMode.NEW_STACK)
                counter = 0

            await asyncio.sleep(2 * 60)
    except asyncio.CancelledError:
        raise


async def msg_instant(user_id: int, manager: BaseDialogManager):
    data = \
        (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token",
                                                               "organization"))[
            0]
    refresh_token, access_token, organization = data[0], data[1], data[2]

    conversations_amount = await get_conversations_amount(user_id=user_id,
                                                          refresh_token=refresh_token,
                                                          access_token=access_token,
                                                          org_id=organization)

    tasks_amount = await get_tasks_amount(user_id=user_id,
                                          refresh_token=refresh_token,
                                          access_token=access_token,
                                          org_id=organization)

    await ActiveUsers.filter(user_id=user_id).update(conversations_amount=conversations_amount,
                                                     tasks_amount=tasks_amount)

    try:
        while True:
            data = \
                (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token",
                                                                       "organization"))[
                    0]
            refresh_token, access_token, organization = data[0], data[1], data[2]

            conversations_amount = \
                (await ActiveUsers.filter(user_id=user_id).values_list("conversations_amount", flat=True))[0]

            tasks_amount = (await ActiveUsers.filter(user_id=user_id).values_list("tasks_amount", flat=True))[0]

            new_tasks_amount = await get_tasks_amount(user_id=user_id,
                                                      refresh_token=refresh_token,
                                                      access_token=access_token,
                                                      org_id=organization)

            new_convers_amount = await get_conversations_amount(user_id=user_id,
                                                                refresh_token=refresh_token,
                                                                access_token=access_token,
                                                                org_id=organization)

            diff_msgs_in_conv = new_convers_amount - conversations_amount

            if diff_msgs_in_conv > 0:
                if [11, 12, 13, 14].__contains__(diff_msgs_in_conv):
                    await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщений!")
                else:
                    match diff_msgs_in_conv % 10:
                        case 1:
                            await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новое сообщение!")
                        case 2 | 3 | 4:
                            await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщения!")
                        case _:
                            await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщений!")

                await ActiveUsers.filter(user_id=user_id).update(new_convs=diff_msgs_in_conv)
                await ActiveUsers.filter(user_id=user_id).update(conversations_amount=new_convers_amount)
                await manager.start(MessagesSG.choose_action, mode=StartMode.RESET_STACK)

            await asyncio.sleep(2)

            diff_tasks = new_tasks_amount - tasks_amount

            if diff_tasks > 0:
                if [11, 12, 13, 14].__contains__(diff_tasks):
                    await MyBot.bot.send_message(user_id, f"У Вас {diff_tasks} новых задач!")
                else:
                    match diff_tasks % 10:
                        case 1:
                            await MyBot.bot.send_message(user_id, f"У Вас {diff_tasks} новая задача!")
                        case 2 | 3 | 4:
                            await MyBot.bot.send_message(user_id, f"У Вас {diff_tasks} новые задачи!")
                        case _:
                            await MyBot.bot.send_message(user_id, f"У Вас {diff_tasks} новых задач!")

                await ActiveUsers.filter(user_id=user_id).update(tasks_amount=new_tasks_amount)
                await ActiveUsers.filter(user_id=user_id).update(new_tasks=diff_tasks)
                await manager.start(TasksSG.choose_action, mode=StartMode.NEW_STACK)

            await asyncio.sleep(2 * 60)
    except asyncio.CancelledError:
        raise


async def loop_notifications_8hrs(user_id, manager):
    loop = asyncio.get_event_loop()
    loop.create_task(msg_8hrs(user_id=user_id, manager=manager), name=str(user_id))


async def loop_notifications_instant(user_id, manager):
    loop = asyncio.get_event_loop()
    loop.create_task(msg_instant(user_id=user_id, manager=manager), name=str(user_id))


async def kill_task(user_id: int):
    print("Пора убивать")
    for task in asyncio.all_tasks():
        if task.get_name() == str(user_id):
            while not task.cancelled() or not task.done():
                print("Kill", task.get_name())
                task.cancel()
                await asyncio.sleep(0.5)


async def is_task_active(user_id: int):
    for task in asyncio.all_tasks():
        if task.get_name() == str(user_id):
            return True
    return False


async def start_notifications(user_id: int, manager: BaseDialogManager):
    eight_hour_notification = \
        (await ActiveUsers.filter(user_id=user_id).values_list("eight_hour_notification", flat=True))[0]
    instant_notification = \
        (await ActiveUsers.filter(user_id=user_id).values_list("instant_notification", flat=True))[0]
    not_notification = \
        (await ActiveUsers.filter(user_id=user_id).values_list("not_notification", flat=True))[0]
    if not eight_hour_notification and not instant_notification and not not_notification:
        await ActiveUsers.filter(user_id=user_id).update(instant_notification=True)
        await loop_notifications_instant(user_id=user_id, manager=manager)
    elif eight_hour_notification:
        await asyncio.wait_for(kill_task(user_id), timeout=None)
        await loop_notifications_8hrs(user_id=user_id, manager=manager)
    elif instant_notification:
        await asyncio.wait_for(kill_task(user_id), timeout=None)
        await loop_notifications_instant(user_id=user_id, manager=manager)
