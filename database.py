import asyncio
import pandas as pd
import psycopg2

from datetime import datetime
from tortoise import Tortoise, fields
from tortoise.models import Model

# Классы ORM

class Situations(Model):
    id = fields.BigIntField(pk=True)
    situation = fields.IntField()
    text = fields.TextField()
    answer = fields.TextField()
    score = fields.IntField()

    class Meta:
        table = "situations"


class Results(Model):
    class Meta:
        unique_together = ("user_id", "try_num")
        table = "results"
    user_id = fields.BigIntField()
    name = fields.TextField()
    try_num = fields.TextField()
    start_time = fields.TextField()
    end_time = fields.TextField()
    c1 = fields.FloatField()
    c2 = fields.FloatField()
    c3 = fields.FloatField()
    c4 = fields.FloatField()
    c5 = fields.FloatField()
    c6 = fields.FloatField()
    c7 = fields.FloatField()
    c8 = fields.FloatField()


async def admin_load():
    conn = psycopg2.connect("postgres://blaehfiylzuywc:771798453e6550bb74ffe3f3d386b9de2ac0183c66d2b3d729ac4fb93591bbaa@ec2-176-34-211-0.eu-west-1.compute.amazonaws.com:5432/d2c4gv7boohhj7", sslmode='require')
    cur = conn.cursor()
    copy = "COPY results TO STDOUT WITH CSV DELIMITER ',' HEADER"
    with open("results.csv", "w") as file:
        cur.copy_expert(copy, file)
    cur.close()

    excel_file = f'test_handball_{datetime.now().strftime("%d-%m-%y_%H-%M-%S")}.xlsx'
    read_file = pd.read_csv('results.csv')
    read_file.to_excel(excel_file, encoding='utf8', index=None, header=True)

    return excel_file

# Инициализация базы данных
async def run():
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": "d2c4gv7boohhj7",
                        "host": "ec2-176-34-211-0.eu-west-1.compute.amazonaws.com",
                        "password": "771798453e6550bb74ffe3f3d386b9de2ac0183c66d2b3d729ac4fb93591bbaa",
                        "port": 5432,
                        "user": "blaehfiylzuywc"
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
