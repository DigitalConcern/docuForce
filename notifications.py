import asyncio
from bot import MyBot
from client import get_tasks_dict
from database import ActiveUsers


async def msg_8hrs(user_id):
    while True:
        await asyncio.sleep(8 * 60 * 60)
        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization",
                                                                      "tasks_amount"))[0]
        refresh_token, access_token, organization, tasks_amount = data[0], data[1], data[2], data[3]

        new_tasks_amount = len(await get_tasks_dict(user_id=user_id,
                                                    refresh_token=refresh_token,
                                                    access_token=access_token,
                                                    org_id=organization))

        diff = new_tasks_amount - tasks_amount
        if diff > 0:
            match diff % 10:
                case 1:
                    if diff != 11:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новая задача!")
                    else:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новых задач!")
                case 2:
                    if diff != 12:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новая задача!")
                    else:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новых задач!")
                case 3:
                    if diff != 13:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новыые задачи!")
                    else:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новых задач!")
                case 4:
                    if diff != 14:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новыые задачи!")
                    else:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новых задач!")
        else:
            await MyBot.bot.send_message(user_id, f"У Вас нет новых задач!")


async def msg_instant(user_id):
    while True:
        await asyncio.sleep(20)
        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization",
                                                                      "tasks_amount"))[0]
        refresh_token, access_token, organization, tasks_amount = data[0], data[1], data[2], data[3]
        new_tasks_amount = len(await get_tasks_dict(user_id=user_id,
                                                    refresh_token=refresh_token,
                                                    access_token=access_token,
                                                    org_id=organization))

        diff = new_tasks_amount - tasks_amount
        if diff > 0:
            match diff % 10:
                case 1:
                    if diff != 11:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новая задача!")
                    else:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новых задач!")
                case 2:
                    if diff != 12:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новая задача!")
                    else:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новых задач!")
                case 3:
                    if diff != 13:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новыые задачи!")
                    else:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новых задач!")
                case 4:
                    if diff != 14:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новыые задачи!")
                    else:
                        await MyBot.bot.send_message(user_id, f"У Вас {diff} новых задач!")


async def loop_notifications_8hrs(user_id):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(msg_8hrs(user_id=user_id))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(msg_8hrs(user_id=user_id))


async def loop_notifications_instant(user_id):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(msg_instant(user_id=user_id))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(msg_instant(user_id=user_id))
