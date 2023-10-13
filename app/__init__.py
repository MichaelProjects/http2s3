import logging
import os

from fastapi import Depends, FastAPI
from app.v1.endpoint import v1_router
from app.lib.conf import set_env


format = "%(asctime)s | %(lineno)d | %(levelname)s | %(funcName)s | %(message)s"
logging.basicConfig(level=logging.ERROR, format=format)

set_env()


app = FastAPI()

app.include_router(v1_router)