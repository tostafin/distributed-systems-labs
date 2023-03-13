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

UNICAST_ASCII_ART: Final[str] = """
 |\\__/,|   (`\\
 |_ _  |.--.) )
 ( T   )     /
(((^_(((/(((_/"""

MULTICAST_ASCII_ART: Final[str] = """
          ____  
        o8%8888,    
      o88%8888888.  
     8'-    -:8888b   
    8'         8888  
   d8.-=. ,==-.:888b  
   >8 `~` :`~' d8888   
   88         ,88888   
   88b. `-~  ':88888  
   888b ~==~ .:88888 
   88888o--:':::8888      
   `88888| :::' 8888b  
   8888^^'       8888b  
  d888           ,%888b.   
 d88%            %%%8--'-.  
/88:.__ ,       _%-' ---  -  
    '''::===..-'   =  --."""
