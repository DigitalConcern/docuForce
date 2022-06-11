import asyncio

from tortoise import Tortoise, fields
from tortoise.models import Model


class ActiveUsers(Model):
    user_id = fields.IntField(pk=True)
    login = fields.TextField()
    password = fields.TextField()
    organization = fields.IntField()

    class Meta:
        table = "users"


async def run():
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": "postgres",
                        "host": "localhost",
                        "password": "12345",
                        "port": 5432,
                        "user": "postgres"
                    }
                }
            },
            "apps": {
                "models": {
                    "models": ["database"],
                    "default_connection": "default",
                }
            },
        }
    )
    await Tortoise.generate_schemas()


async def loop_db():
    loop = asyncio.get_event_loop()
    loop.create_task(run())
