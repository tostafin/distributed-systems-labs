import socket
import signal
import sys

from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from typing import Set, Tuple

from constants import MAX_NUM_OF_CLIENTS, IP, PORT, MAX_BUF_SIZE, MESSAGE, ENCODING, INIT_MSG


def signal_handler(sig, frame):
    print("\nServer finished.")
    sys.exit(0)


tcp_clients: Set[socket.socket] = set()  # TODO: add locks
def handle_single_tcp_client(client: socket.socket) -> None:
    buf: bytes
    while buf := client.recv(MAX_BUF_SIZE):
        if (message := buf.decode(ENCODING)) == INIT_MSG:
            print("New TCP client has connected.")
            print(client)
            tcp_clients.add(client)
        else:
            nick, _, payload = message.partition(":")
            print(f"Message from {nick}: {payload}")

            for c in tcp_clients:
                if c != client:
                    c.sendall(bytes(MESSAGE.format(nick=nick, message=payload), ENCODING))

    tcp_clients.remove(client)


def handle_tcp_client() -> None:
    with ThreadPoolExecutor(max_workers=MAX_NUM_OF_CLIENTS) as executor:
        # create an INET, STREAMing socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # bind the socket to the localhost and a port
            server_socket.bind((IP, PORT))
            # become a server socket
            server_socket.listen(MAX_NUM_OF_CLIENTS)
            while True:
                # accept connections from outside
                client_socket, _ = server_socket.accept()
                print(_)
                # now do something with the client_socket
                executor.submit(handle_single_tcp_client, client_socket)


def handle_udp_client() -> None:
    udp_clients: Set[Tuple[str, int]] = set()
    # create an INET, datagram socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # bind the socket to the localhost and a port
        server_socket.bind((IP, PORT))
        while True:
            buf, address = server_socket.recvfrom(MAX_BUF_SIZE)

            if (message := buf.decode(ENCODING)) == INIT_MSG:
                udp_clients.add(address)
                print("New UDP client connected.")

            else:
                nick, _, payload = message.partition(":")
                print(f"Message from {nick}: {payload}")

                for c in udp_clients:
                    if c != address:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
                            client_socket.sendto(bytes(f"{nick}:{payload}", ENCODING), (c[0], c[1]))


def main() -> int:
    signal.signal(signal.SIGINT, signal_handler)

    tcp_client_handler = Thread(target=handle_tcp_client, daemon=True)
    udp_client_handler = Thread(target=handle_udp_client, daemon=True)

    tcp_client_handler.start()
    udp_client_handler.start()

    tcp_client_handler.join()
    udp_client_handler.join()

    return 0


if __name__ == "__main__":
    main()
