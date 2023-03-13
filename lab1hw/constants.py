from typing import Final

MAX_NUM_OF_CLIENTS: Final[int] = 2

IP: Final[str] = "localhost"
PORT: Final[int] = 8000
MULTICAST_TTL: Final[int] = 2

MAX_BUF_SIZE: Final[int] = 1024

MESSAGE: Final[str] = "{nick}:{message}"
ENCODING: Final[str] = "utf-8"
INIT_MSG: Final[str] = "INIT"

UDP_UNICAST_MSG: Final[str] = "U"
UDP_MULTICAST_MSG: Final[str] = "M"

ASCII_ART: Final[str] = """
 |\\__/,|   (`\\
 |_ _  |.--.) )
 ( T   )     /
(((^_(((/(((_/"""
