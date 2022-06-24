import asyncio
from collections import defaultdict

from aiogram.types import ParseMode
from aiogram_dialog import DialogManager, StartMode

from bot import MyBot
from client import get_tasks_dict, get_conversations_dict
from database import ActiveUsers

from dialogs.tasks_dialog import TasksSG
from dialogs.messages_dialog import MessagesSG


async def old_msg_8hrs(user_id: int, manager: DialogManager):
    counter = 0
    messages_in_conv = defaultdict(int)
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
                            # await manager.start(MessagesSG.choose_action)
                            msg_arr = new_conversations[conv_key][6][:diff_msgs_in_conv]
                            micro_text = f"По документу {new_conversations[conv_key][1]}" \
                                         f"{new_conversations[conv_key][4]}" \
                                         f"{new_conversations[conv_key][3]}" \
                                         f"{new_conversations[conv_key][2]}" \
                                         f"{new_conversations[conv_key][0]}" \
                                         f"{new_conversations[conv_key][5]}" \
                                         f'<i>{"".join(reversed(msg_arr))}</i>' \
                                         f"{new_conversations[conv_key][7]}"
                            await MyBot.bot.send_message(user_id, text=micro_text, parse_mode=ParseMode.HTML)
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
                # await manager.start(TasksSG.choose_action, mode=StartMode.RESET_STACK)
                text_not_task = "Ваши новые задачи: \n"
                for ii in range(diff_tasks - 1, -1, -1):
                    i = str(ii)
                    text_not_task += f"{new_tasks_dict[i][1]}{new_tasks_dict[i][5]} {new_tasks_dict[i][4]}{new_tasks_dict[i][2]}{new_tasks_dict[i][0]}{new_tasks_dict[i][6]}{new_tasks_dict[i][7]}\n\n"

                await MyBot.bot.send_message(user_id, text_not_task, parse_mode=ParseMode.HTML)
            else:
                await MyBot.bot.send_message(user_id, f"Новых сообщений нет!")
            counter = 0
async def old_msg_8hrs(user_id: int, manager: DialogManager):
    counter = 0
    messages_in_conv = defaultdict(int)
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
                            # await manager.start(MessagesSG.choose_action)
                            msg_arr = new_conversations[conv_key][6][:diff_msgs_in_conv]
                            micro_text = f"По документу {new_conversations[conv_key][1]}" \
                                         f"{new_conversations[conv_key][4]}" \
                                         f"{new_conversations[conv_key][3]}" \
                                         f"{new_conversations[conv_key][2]}" \
                                         f"{new_conversations[conv_key][0]}" \
                                         f"{new_conversations[conv_key][5]}" \
                                         f'<i>{"".join(reversed(msg_arr))}</i>' \
                                         f"{new_conversations[conv_key][7]}"
                            await MyBot.bot.send_message(user_id, text=micro_text, parse_mode=ParseMode.HTML)
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
                # await manager.start(TasksSG.choose_action, mode=StartMode.RESET_STACK)
                text_not_task = "Ваши новые задачи: \n"
                for ii in range(diff_tasks - 1, -1, -1):
                    i = str(ii)
                    text_not_task += f"{new_tasks_dict[i][1]}{new_tasks_dict[i][5]} {new_tasks_dict[i][4]}{new_tasks_dict[i][2]}{new_tasks_dict[i][0]}{new_tasks_dict[i][6]}{new_tasks_dict[i][7]}\n\n"

                await MyBot.bot.send_message(user_id, text_not_task, parse_mode=ParseMode.HTML)
            else:
                await MyBot.bot.send_message(user_id, f"Новых сообщений нет!")
            counter = 0


async def old_msg_instant(user_id: int, manager: DialogManager):
    messages_in_conv = defaultdict(int)
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
            messages_in_conv[conv_key] = conversations[conv_key][10]

        await asyncio.sleep(5*60)

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
                                    await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новое сообщение!")
                                case 2 | 3 | 4:
                                    await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщения!")
                                case _:
                                    await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщений!")
                        # await manager.start(MessagesSG.choose_action)
                        msg_arr = new_conversations[conv_key][6][:diff_msgs_in_conv]
                        micro_text = f"По документу {new_conversations[conv_key][1]}" \
                                     f"{new_conversations[conv_key][4]}" \
                                     f"{new_conversations[conv_key][3]}" \
                                     f"{new_conversations[conv_key][2]}" \
                                     f"{new_conversations[conv_key][0]}" \
                                     f"{new_conversations[conv_key][5]}" \
                                     f'<i>{"".join(reversed(msg_arr))}</i>' \
                                     f"{new_conversations[conv_key][7]}"
                        await MyBot.bot.send_message(user_id, text=micro_text, parse_mode=ParseMode.HTML)
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
            # await manager.start(TasksSG.choose_action, mode=StartMode.RESET_STACK)
            text_not_task = "Ваши новые задачи: \n"
            for ii in range(diff_tasks - 1, -1, -1):
                i = str(ii)
                text_not_task += f"{new_tasks_dict[i][1]}{new_tasks_dict[i][5]} {new_tasks_dict[i][4]}{new_tasks_dict[i][2]}{new_tasks_dict[i][0]}{new_tasks_dict[i][6]}{new_tasks_dict[i][7]}\n\n"

            await MyBot.bot.send_message(user_id, text_not_task, parse_mode=ParseMode.HTML)
        # else:
        #     await MyBot.bot.send_message(user_id, f"У Вас нет новых задач!")

        # diff_conv = new_convers_amount - convers_amount
        # if diff_conv > 0:
        #     if [11, 12, 13, 14].__contains__(diff_conv):
        #         await MyBot.bot.send_message(user_id, f"У Вас {diff_conv} новых обсуждений документов!")
        #     else:
        #         match diff_conv % 10:
        #             case 1:
        #                 await MyBot.bot.send_message(user_id, f"У Вас {diff_conv} новое обсуждение документов!")
        #             case 2 | 3 | 4:
        #                 await MyBot.bot.send_message(user_id, f"У Вас {diff_conv} новых обсуждения документов!")
        #             case _:
        #                 await MyBot.bot.send_message(user_id, f"У Вас {diff_conv} новых обсуждений документов!")
        #     for ii in range(diff_conv - 1, -1, -1):
        #         micro_text = f"По документу {new_conversations[conv_key][1]}" \
        #                      f"{new_conversations[conv_key][4]}" \
        #                      f"{new_conversations[conv_key][3]}" \
        #                      f"{new_conversations[conv_key][2]}" \
        #                      f"{new_conversations[conv_key][0]}" \
        #                      f"{new_conversations[conv_key][5]}" \
        #                      f'<i>{"".join(reversed(msg_arr))}</i>' \
        #                      f"{new_conversations[conv_key][7]}"
        # await manager.bg().start(MessagesSG.choose_action)
        # else:
        #     await MyBot.bot.send_message(user_id, f"И нет новых сообщений!")

async def msg_instant(user_id: int, manager: DialogManager):
    messages_in_conv = defaultdict(int)
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
            messages_in_conv[conv_key] = conversations[conv_key][10]

        await asyncio.sleep(5*60)

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
        conv_counter=0
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
                                    await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новое сообщение!")
                                case 2 | 3 | 4:
                                    await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщения!")
                                case _:
                                    await MyBot.bot.send_message(user_id, f"У Вас {diff_msgs_in_conv} новых сообщений!")
                        await ActiveUsers.filter(user_id=user_id).update(new_convs=diff_msgs_in_conv)
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

async def loop_notifications_8hrs(user_id, manager):
    loop = asyncio.get_event_loop()
    # loop.create_task(msg_8hrs(user_id=user_id, manager=manager), name=str(user_id))


async def loop_notifications_instant(user_id, manager):
    loop = asyncio.get_event_loop()
    # loop.create_task(msg_instant(user_id=user_id, manager=manager), name=str(user_id))
