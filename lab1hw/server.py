import socket
import signal
import sys
import struct

from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
from typing import Set, Tuple

from constants import IP, PORT, MAX_BUF_SIZE, MESSAGE, ENCODING, INIT_MSG


def signal_handler(sig, frame):
    print("\nServer finished.")
    sys.exit(0)


tcp_clients: Set[socket.socket] = set()
tcp_clients_lock = Lock()
def handle_single_tcp_client(client: socket.socket) -> None:
    buf: bytes
    while buf := client.recv(MAX_BUF_SIZE):
        if (message := buf.decode(ENCODING)) == INIT_MSG:
            print("New TCP client has connected.")
            with tcp_clients_lock:
                tcp_clients.add(client)
        else:
            nick, _, payload = message.partition(":")
            print(f"TCP message from {nick}: {payload}")

            print("Sending to other clients...")
            with tcp_clients_lock:
                for c in tcp_clients:
                    if c != client:
                        c.sendall(bytes(MESSAGE.format(nick=nick, message=payload), ENCODING))

    with tcp_clients_lock:
        tcp_clients.remove(client)


def receive_tcp_messages(max_num_of_clients: int) -> None:
    with ThreadPoolExecutor(max_workers=max_num_of_clients) as executor:
        # create an INET, STREAMing socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # bind the socket to the localhost and a port
            server_socket.bind((IP, PORT))
            # become a server socket
            server_socket.listen(max_num_of_clients)
            while True:
                # accept connections from outside
                client_socket, _ = server_socket.accept()
                # now do something with the client_socket
                executor.submit(handle_single_tcp_client, client_socket)


def receive_udp_messages() -> None:
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
                print(f"UDP message from {nick}: {payload}")

                print("Sending to other clients...")
                for c in udp_clients:
                    if c != address:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
                            client_socket.sendto(bytes(f"{nick}:{payload}", ENCODING), (c[0], c[1]))


def receive_udp_multicast_messages(multicast_address: str, multicast_port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as\
            udp_multicast_socket:
        udp_multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        udp_multicast_socket.bind((multicast_address, multicast_port))

        mreq = struct.pack("4sl", socket.inet_aton(multicast_address), socket.INADDR_ANY)

        udp_multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            buf, _ = udp_multicast_socket.recvfrom(MAX_BUF_SIZE)
            nick, _, payload = buf.decode(ENCODING).partition(":")
            print(f"Multicast message from {nick}: {payload}")


def main() -> int:
    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) != 4:
        print(
            f"Usage: python {sys.argv[0]} <max_num_of_clients> <multicast_address> <multicast_port>"
        )
        sys.exit(0)
    max_num_of_clients = int(sys.argv[1])
    multicast_address, multicast_port = sys.argv[2], int(sys.argv[3])

    tcp_client_handler = Thread(
        target=receive_tcp_messages, args=(max_num_of_clients,), daemon=True
    )
    udp_client_handler = Thread(target=receive_udp_messages, daemon=True)
    udp_multicast_handler = Thread(
        target=receive_udp_multicast_messages, args=(multicast_address, multicast_port), daemon=True
    )

    tcp_client_handler.start()
    udp_client_handler.start()
    udp_multicast_handler.start()

    print("Server ready.")

    tcp_client_handler.join()
    udp_client_handler.join()
    udp_multicast_handler.join()

    return 0


if __name__ == "__main__":
    main()
