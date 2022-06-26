import asyncio
import logging
import os
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.DEBUG)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "based.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

app = FastAPI()
