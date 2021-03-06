import logging
import os

import asyncio
from multiprocessing import Process

import uvicorn
from django.core.asgi import get_asgi_application

logging.basicConfig(level=logging.DEBUG)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "based.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


class MyServer:
    app = get_asgi_application()

    config = uvicorn.Config(host='0.0.0.0', app=app, loop=loop, port=8001)
    # config = uvicorn.Config(app=app, loop=loop, port=8001)
    server = uvicorn.Server(config=config)

    @classmethod
    def run(cls):
        asyncio.run(cls.server.serve())


def run_app():
    server = Process(target=MyServer.run)
    server.start()


if __name__ == "__main__":
    run_app()
