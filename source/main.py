import asyncio
import logging
import os
import uvicorn
from django.core.asgi import get_asgi_application

logging.basicConfig(level=logging.DEBUG)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "based.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

app = get_asgi_application()
