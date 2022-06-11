import asyncio
from bot import MyBot
from database import loop_db
import auth_dialog


async def main():
    await loop_db()
    await MyBot.run_bot()


if __name__ == '__main__':
    asyncio.run(main())
