import asyncio
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
    tasks_amount = 0
    messages_amount = 0
    while True:

        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization",
                                                                      "tasks_amount", "conversations_amount"))[0]
        refresh_token, access_token, organization = data[0], data[1], data[2]
        if counter == 0:
            tasks_amount, messages_amount = data[3], data[4]

        new_tasks_amount = len(await get_tasks_dict(user_id=user_id,
                                                    refresh_token=refresh_token,
                                                    access_token=access_token,
                                                    org_id=organization))

        new_msg_amount = len(await get_conversations_dict(user_id=user_id,
                                                          refresh_token=refresh_token,
                                                          access_token=access_token,
                                                          org_id=organization))

        await ActiveUsers.filter(user_id=user_id).update(tasks_amount=new_tasks_amount, messages_amount=new_msg_amount)
        counter += 1
        if counter == 96:  # (8*60*60)/5
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
                await manager.start(TasksSG.choose_action, mode=StartMode.RESET_STACK)
            else:
                await MyBot.bot.send_message(user_id, f"У Вас нет новых задач!")

            diff_msg = new_msg_amount - messages_amount
            if diff_msg > 0:
                if [11, 12, 13, 14].__contains__(diff_msg):
                    await MyBot.bot.send_message(user_id, f"И {diff_msg} новых сообщений!")
                else:
                    match diff_msg % 10:
                        case 1:
                            await MyBot.bot.send_message(user_id, f"И {diff_msg} новое сообщение!")
                        case 2 | 3 | 4:
                            await MyBot.bot.send_message(user_id, f"И {diff_msg} новых сообщения!")
                        case _:
                            await MyBot.bot.send_message(user_id, f"И {diff_msg} новых сообщений!")
                await manager.start(MessagesSG.choose_action)
            else:
                await MyBot.bot.send_message(user_id, f"И нет новых сообщений!")

            counter = 0
        await asyncio.sleep(5 * 60)


async def msg_instant(user_id: int, manager: DialogManager):
    messages_in_conv = defaultdict(list)
    while True:
        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization",
                                                                      "tasks_amount", "conversations_amount"))[0]
        refresh_token, access_token, organization = data[0], data[1], data[2]
        tasks_amount, convers_amount = data[3], data[4]

        conversations = await get_conversations_dict(user_id=user_id,
                                                     refresh_token=refresh_token,
                                                     access_token=access_token,
                                                     org_id=organization)

        for conv_key in conversations.keys():
            messages_in_conv[conv_key].append(conversations[conv_key][10])

        await asyncio.sleep(25)

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
                                    await MyBot.bot.send_message(user_id, f"И {diff_msgs_in_conv} новое сообщение!")
                                case 2 | 3 | 4:
                                    await MyBot.bot.send_message(user_id, f"И {diff_msgs_in_conv} новых сообщения!")
                                case _:
                                    await MyBot.bot.send_message(user_id, f"И {diff_msgs_in_conv} новых сообщений!")
                        await manager.bg().start(MessagesSG.choose_action)
            except KeyError:
                pass

        await ActiveUsers.filter(user_id=user_id).update(tasks_amount=new_tasks_amount,
                                                         conversations_amount=new_convers_amount)
        diff_tasks = new_tasks_amount - tasks_amount
        # text_not_task = ""
        # for i in range(diff_tasks):
        #     text_not_task += text_task[i]
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
            await manager.bg().start(TasksSG.choose_action, mode=StartMode.RESET_STACK)

            # await MyBot.bot.send_message(user_id, text_not_task, parse_mode=ParseMode.HTML)
        # else:
        #     await MyBot.bot.send_message(user_id, f"У Вас нет новых задач!")

        diff_conv = new_convers_amount - convers_amount
        if diff_conv > 0:
            if [11, 12, 13, 14].__contains__(diff_conv):
                await MyBot.bot.send_message(user_id, f"И {diff_conv} новых сообщений!")
            else:
                match diff_conv % 10:
                    case 1:
                        await MyBot.bot.send_message(user_id, f"И {diff_conv} новое сообщение!")
                    case 2 | 3 | 4:
                        await MyBot.bot.send_message(user_id, f"И {diff_conv} новых сообщения!")
                    case _:
                        await MyBot.bot.send_message(user_id, f"И {diff_conv} новых сообщений!")
            await manager.bg().start(MessagesSG.choose_action)
        # else:
        #     await MyBot.bot.send_message(user_id, f"И нет новых сообщений!")


async def loop_notifications_8hrs(user_id, manager):
    loop = asyncio.get_event_loop()
    loop.create_task(msg_8hrs(user_id=user_id, manager=manager), name=str(user_id))


async def loop_notifications_instant(user_id, manager):
    loop = asyncio.get_event_loop()
    loop.create_task(msg_instant(user_id=user_id, manager=manager), name=str(user_id))
