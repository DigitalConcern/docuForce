import asyncio
from bot import MyBot
from client import get_tasks_dict, get_messages_dict
from database import ActiveUsers


async def msg_8hrs(user_id):
    counter = 0
    tasks_amount = 0
    messages_amount = 0
    while True:

        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization",
                                                                      "tasks_amount", "messages_amount"))[0]
        refresh_token, access_token, organization = data[0], data[1], data[2]
        if counter == 0:
            tasks_amount, messages_amount = data[3], data[4]

        new_tasks_amount = len(await get_tasks_dict(user_id=user_id,
                                                    refresh_token=refresh_token,
                                                    access_token=access_token,
                                                    org_id=organization))

        new_msg_amount = len(await get_messages_dict(user_id=user_id,
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
            else:
                await MyBot.bot.send_message(user_id, f"И нет новых сообщений!")

            counter = 0
        await asyncio.sleep(5 * 60)


async def msg_instant(user_id):
    while True:
        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization",
                                                                      "tasks_amount", "messages_amount"))[0]
        refresh_token, access_token, organization = data[0], data[1], data[2]
        tasks_amount, messages_amount = data[3], data[4]
        await asyncio.sleep(5 * 60)

        new_tasks_dict = await get_tasks_dict(user_id=user_id,
                                              refresh_token=refresh_token,
                                              access_token=access_token,
                                              org_id=organization)
        new_tasks_amount = len(new_tasks_dict)
        new_msg_dict = await get_messages_dict(user_id=user_id,
                                               refresh_token=refresh_token,
                                               access_token=access_token,
                                               org_id=organization)
        new_msg_amount = len(new_msg_dict)

        await ActiveUsers.filter(user_id=user_id).update(tasks_amount=new_tasks_amount, messages_amount=new_msg_amount)
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
        # else:
        #     await MyBot.bot.send_message(user_id, f"У Вас нет новых задач!")

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
        # else:
        #     await MyBot.bot.send_message(user_id, f"И нет новых сообщений!")


async def loop_notifications_8hrs(user_id):
    loop = asyncio.get_event_loop()
    loop.create_task(msg_8hrs(user_id=user_id), name=str(user_id))


async def loop_notifications_instant(user_id):
    loop = asyncio.get_event_loop()
    loop.create_task(msg_instant(user_id=user_id), name=str(user_id))
