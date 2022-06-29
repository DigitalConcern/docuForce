import asyncio
import os

from tortoise import Tortoise, fields
from tortoise.models import Model


class Stats(Model):
    users = fields.IntField(default=0)
    documents = fields.IntField(default=0)
    command_tasks = fields.IntField(default=0)
    command_documents = fields.IntField(default=0)
    command_search = fields.IntField(default=0)
    command_messages = fields.IntField(default=0)
    tasks_done = fields.IntField(default=0)
    messages_done = fields.IntField(default=0)

    class Meta:
        table = "stats"


class ActiveUsers(Model):
    user_id = fields.BigIntField(pk=True)
    user_org_id = fields.UUIDField(null=True)
    login = fields.TextField()
    password = fields.TextField()
    organization = fields.UUIDField(null=True)
    refresh_token = fields.TextField()
    access_token = fields.TextField()
    current_document_id = fields.TextField(null=True)
    tasks_amount = fields.IntField(default=0)
    conversations_amount = fields.IntField(default=0)
    eight_hour_notification = fields.BooleanField(default=False)
    instant_notification = fields.BooleanField(default=True)
    not_notification = fields.BooleanField(default=False)
    new_tasks = fields.IntField(default=0)
    new_convs = fields.IntField(default=0)

    class Meta:
        table = "users"


async def run():
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database":  os.environ.get('POSTGRES_NAME'),
                        "host": "db",
                        "password": os.environ.get('POSTGRES_PASSWORD'),
                        "port": 5432,
                        "user": os.environ.get('POSTGRES_USER'),
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


# async def run():
#     await Tortoise.init(
#         config={
#             "connections": {
#                 "default": {
#                     "engine": "tortoise.backends.asyncpg",
#                     "credentials": {
#                         "database": "postgres",
#                         "host": "localhost",
#                         "password": "12345",
#                         "port": 5432,
#                         "user": "postgres"
#                     }
#                 }
#             },
#             "apps": {
#                 "models": {
#                     "models": ["database"],
#                     "default_connection": "default",
#                 }
#             },
#         }
#     )
#     await Tortoise.generate_schemas()


async def loop_db():
    loop = asyncio.get_event_loop()
    loop.create_task(run())
