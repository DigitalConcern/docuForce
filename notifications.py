import asyncio
from asyncio import CancelledError
from collections import defaultdict

from aiogram.types import ParseMode
from aiogram_dialog import DialogManager, StartMode

from bot import MyBot
from client import get_tasks_dict, get_conversations_dict
from database import ActiveUsers

from dialogs.tasks_dialog import TasksSG
from dialogs.messages_dialog import MessagesSG




async def msg_8hrs(user_id: int, manager: DialogManager):
    counter = 0
    messages_in_conv = defaultdict(int)
    while True:
        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization"))[
            0]
        refresh_token, access_token, organization = data[0], data[1], data[2]

        conversations = await get_conversations_dict(user_id=user_id,
                                                     refresh_token=refresh_token,
                                                     access_token=access_token,
                                                     org_id=organization)

        tasks_dict = await get_tasks_dict(user_id=user_id,
                                          refresh_token=refresh_token,
                                          access_token=access_token,
                                          org_id=organization)
        tasks_amount = len(tasks_dict)

        for conv_key in conversations.keys():
            messages_in_conv[conv_key] = conversations[conv_key][10]

        await asyncio.sleep(5 * 60 * 5)

        new_tasks_dict = await get_tasks_dict(user_id=user_id,
                                              refresh_token=refresh_token,
                                              access_token=access_token,
                                              org_id=organization)
        new_tasks_amount = len(new_tasks_dict)

        new_conversations = await get_conversations_dict(user_id=user_id,
                                                         refresh_token=refresh_token,
                                                         access_token=access_token,
                                                         org_id=organization)

        new_convers_amount = len(new_conversations)
        counter += 1
        if counter >= 96:
            for conv_key in new_conversations.keys():
                try:
                    if messages_in_conv[conv_key] < new_conversations[conv_key][10]:
                        diff_msgs_in_conv = new_conversations[conv_key][10] - messages_in_conv[conv_key]
                        if diff_msgs_in_conv > 0:
                            if [11, 12, 13, 14].__contains__(diff_msgs_in_conv):
                                await MyBot.bot.send_message(user_id, f"И {diff_msgs_in_conv} новых сообщений!")
                            else:
                                match diff_msgs_in_conv % 10:
                                    case 1:
                                        await MyBot.bot.send_message(user_id,
                                                                     f"У Вас {diff_msgs_in_conv} новое сообщение!")
                                    case 2 | 3 | 4:
                                        await MyBot.bot.send_message(user_id,
                                                                     f"У Вас {diff_msgs_in_conv} новых сообщения!")
                                    case _:
                                        await MyBot.bot.send_message(user_id,
                                                                     f"У Вас {diff_msgs_in_conv} новых сообщений!")
                            await manager.start(MessagesSG.choose_action)
                        else:
                            await MyBot.bot.send_message(user_id, f"Новых сообщений нет!")
                except KeyError:
                    pass

            await ActiveUsers.filter(user_id=user_id).update(tasks_amount=new_tasks_amount,
                                                             conversations_amount=new_convers_amount)
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
                await manager.start(TasksSG.choose_action)
            else:
                await MyBot.bot.send_message(user_id, f"Новых сообщений нет!")
            counter = 0



async def msg_instant(user_id: int, manager: DialogManager):
    messages_in_conv = defaultdict(int)
    while True:
        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization"))[
            0]
        refresh_token, access_token, organization = data[0], data[1], data[2]

        conversations = await get_conversations_dict(user_id=user_id,
                                                     refresh_token=refresh_token,
                                                     access_token=access_token,
                                                     org_id=organization)

        for conv_key in conversations.keys():
            messages_in_conv[conv_key] = conversations[conv_key][10]

        tasks_dict = await get_tasks_dict(user_id=user_id,
                                          refresh_token=refresh_token,
                                          access_token=access_token,
                                          org_id=organization)
        tasks_amount = len(tasks_dict)

        await asyncio.sleep(30)

        new_tasks_dict = await get_tasks_dict(user_id=user_id,
                                              refresh_token=refresh_token,
                                              access_token=access_token,
                                              org_id=organization)
        new_tasks_amount = len(new_tasks_dict)

        new_conversations = await get_conversations_dict(user_id=user_id,
                                                         refresh_token=refresh_token,
                                                         access_token=access_token,
                                                         org_id=organization)

        new_convers_amount = len(new_conversations)
        try:
            diff_msgs_in_conv = len(new_conversations) - len(messages_in_conv)
            if diff_msgs_in_conv > 0:
                if [11, 12, 13, 14].__contains__(diff_msgs_in_conv):
                    await MyBot.bot.send_message(user_id, f"И {diff_msgs_in_conv} новых сообщений!")
                else:
                    match diff_msgs_in_conv % 10:
                        case 1:
                            await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новое сообщение!")
                        case 2 | 3 | 4:
                            await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщения!")
                        case _:
                            await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщений!")

                await ActiveUsers.filter(user_id=user_id).update(new_convs=diff_msgs_in_conv)
                await manager.start(MessagesSG.choose_action, mode=StartMode.NEW_STACK)
        except KeyError:
            pass

        await ActiveUsers.filter(user_id=user_id).update(tasks_amount=new_tasks_amount,
                                                         conversations_amount=new_convers_amount)
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

            await ActiveUsers.filter(user_id=user_id).update(new_tasks=diff_tasks)
            await manager.start(TasksSG.choose_action, mode=StartMode.NEW_STACK)


async def loop_notifications_8hrs(user_id, manager):
    loop = asyncio.get_event_loop()
    loop.create_task(msg_8hrs(user_id=user_id, manager=manager), name=str(user_id))


async def loop_notifications_instant(user_id, manager):
    loop = asyncio.get_event_loop()
    loop.create_task(msg_instant(user_id=user_id, manager=manager), name=str(user_id))


async def kill_task(user_id: int):

    for task in asyncio.all_tasks():
        if task.get_name() == str(user_id):
            task.cancel()



async def start_notifications(user_id: int, manager: DialogManager):
    eight_hour_notification = \
        (await ActiveUsers.filter(user_id=user_id).values_list("eight_hour_notification", flat=True))[0]
    instant_notification = \
        (await ActiveUsers.filter(user_id=user_id).values_list("instant_notification", flat=True))[0]
    not_notification = \
        (await ActiveUsers.filter(user_id=user_id).values_list("not_notification", flat=True))[0]
    if not eight_hour_notification and not instant_notification and not not_notification:
        await ActiveUsers.filter(user_id=user_id).update(instant_notification=True)
        await loop_notifications_instant(user_id=user_id, manager=manager.bg())
    elif eight_hour_notification:
        await kill_task(user_id)
        await loop_notifications_8hrs(user_id=user_id, manager=manager.bg())
    elif instant_notification:
        await kill_task(user_id)
        await loop_notifications_instant(user_id=user_id, manager=manager.bg())
