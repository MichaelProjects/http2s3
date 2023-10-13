import os

from app.lib.conf import set_env

import uvicorn

set_env()


host: str = os.environ["host"]
port: int = int(os.environ["port"])

if __name__ == '__main__':
    uvicorn.run("app:app", host=host, port=port)