import asyncio
from bot import MyBot
from client import get_tasks_dict
from database import ActiveUsers


async def msg_8hrs(user_id):
    counter = 0
    tasks_amount = 0
    while True:

        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization",
                                                                      "tasks_amount"))[0]
        refresh_token, access_token, organization = data[0], data[1], data[2]
        if counter == 0:
            tasks_amount = data[3]

        new_tasks_amount = len(await get_tasks_dict(user_id=user_id,
                                                    refresh_token=refresh_token,
                                                    access_token=access_token,
                                                    org_id=organization))

        await ActiveUsers.filter(user_id=user_id).update(tasks_amount=new_tasks_amount)
        counter += 1
        if counter == 96:  # (8*60*60)/5
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
            counter = 0
        await asyncio.sleep(5 * 60)


async def msg_instant(user_id):
    while True:
        data = (await ActiveUsers.filter(user_id=user_id).values_list("refresh_token", "access_token", "organization",
                                                                      "tasks_amount"))[0]
        refresh_token, access_token, organization, tasks_amount = data[0], data[1], data[2], data[3]

        await asyncio.sleep(20)

        new_tasks_amount = len(await get_tasks_dict(user_id=user_id,
                                                    refresh_token=refresh_token,
                                                    access_token=access_token,
                                                    org_id=organization))

        await ActiveUsers.filter(user_id=user_id).update(tasks_amount=new_tasks_amount)

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
    loop = asyncio.get_event_loop()
    loop.create_task(msg_8hrs(user_id=user_id))


async def loop_notifications_instant(user_id):
    loop = asyncio.get_event_loop()
    loop.create_task(msg_instant(user_id=user_id))
