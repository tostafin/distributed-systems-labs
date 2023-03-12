import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Set

from constants import NUM_OF_CLIENTS, IP, PORT, MAX_BUF_SIZE, MESSAGE, ENCODING, INIT_MSG


clients: Set[socket.socket] = set()
def handle_client(client: socket.socket) -> None:
    global clients
    buf: bytes
    while buf := client.recv(MAX_BUF_SIZE):
        if (message := buf.decode(ENCODING)) == INIT_MSG:
            print(client)
            clients.add(client)
        else:
            nick, _, payload = message.partition(":")
            print(f"Message from {nick}: {payload}")

            for c in clients:
                print(c, client)
                if c != client:
                    c.sendall(bytes(MESSAGE.format(nick=nick, message=payload), ENCODING))

    clients.remove(client)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=NUM_OF_CLIENTS) as executor:
        # create an INET, STREAMing socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # bind the socket to the localhost and a port
            server_socket.bind((IP, PORT))
            # become a server socket
            server_socket.listen()
            try:
                while True:
                    # accept connections from outside
                    client_socket, address = server_socket.accept()
                    # now do something with the client_socket
                    executor.submit(handle_client, client_socket)

            except KeyboardInterrupt:
                print("Server finished")
