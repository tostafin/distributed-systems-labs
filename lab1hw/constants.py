from typing import Final

NUM_OF_CLIENTS: Final[int] = 2

IP: Final[str] = "localhost"
PORT: Final[int] = 8000

MAX_BUF_SIZE: Final[int] = 1024  # TODO: include nick and colon size, assert here

MESSAGE: Final[str] = "{nick}:{message}"
ENCODING: Final[str] = "utf-8"
INIT_MSG: Final[str] = "INIT"
