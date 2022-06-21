import asyncio

from tortoise import Tortoise, fields
from tortoise.models import Model


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

    class Meta:
        table = "users"


async def run():
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": "d21crbfi20lfgt",
                        "host": "ec2-52-212-228-71.eu-west-1.compute.amazonaws.com",
                        "password": "78ebf737332e11b62f868e64a5a1445d523d768b95deb51b148127f01ee0b026",
                        "port": 5432,
                        "user": "ifkppiqumhvrja"
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
