import asyncio

async def msg():
    while True:
        print("MESSAGE")
        await asyncio.sleep(5)


async def loop_notifications():
    loop = asyncio.get_event_loop()
    loop.create_task(msg())
    await asyncio.sleep(1)