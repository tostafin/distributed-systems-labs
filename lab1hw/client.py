import socket
import signal
import sys

from threading import Thread

from constants import IP, PORT, MULTICAST_TTL, MAX_BUF_SIZE, MESSAGE, ENCODING, INIT_MSG, UDP_UNICAST_MSG, UDP_MULTICAST_MSG, ASCII_ART


def signal_handler(sig, frame):
    print("\nClient finished.")
    sys.exit(0)


def receive_data_from_server(client: socket.socket) -> None:
    buf: bytes
    while buf := client.recv(MAX_BUF_SIZE):
        nick, _, message = buf.decode(ENCODING).partition(":")
        print(f"Message from {nick}: {message}")


def handle_client(nick: str, udp_unicast_socket: socket.socket, udp_multicast_socket: socket.socket,
                  multicast_address: str, multicast_port: int) -> None:
    # create an INET, STREAMing socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # now connect to the localhost
        client_socket.connect((IP, PORT))

        client_socket.sendall(bytes(INIT_MSG, ENCODING))
        handle_sending_udp_unicast(nick, udp_unicast_socket, True)
        print("You're connected to the server. You can now send and receive messages.")

        server_data_receiver = Thread(
            target=receive_data_from_server,
            args=(client_socket,),
            daemon=True
        )
        server_data_receiver.start()

        max_msg_len = MAX_BUF_SIZE - len(nick) - 1
        while True:
            message = input()
            if message == UDP_UNICAST_MSG:
                handle_sending_udp_unicast(nick, udp_unicast_socket, False)
                continue
            if message == UDP_MULTICAST_MSG:
                handle_sending_udp_multicast(
                    nick, udp_multicast_socket, multicast_address, multicast_port
                )
                continue
            if len(message) <= max_msg_len:
                client_socket.sendall(bytes(MESSAGE.format(
                    nick=nick, message=message), ENCODING))
            else:
                print(f"Message too long, maximum {max_msg_len} characters.")


def handle_sending_udp_unicast(nick: str, udp_unicast_socket: socket.socket, init: bool) -> None:
    if init:
        udp_unicast_socket.sendto(bytes(INIT_MSG, ENCODING), (IP, PORT))
    else:
        udp_unicast_socket.sendto(bytes(f"{nick}:{ASCII_ART}", ENCODING), (IP, PORT))


def handle_receiving_udp_unicast(udp_unicast_socket: socket.socket) -> None:
    while True:
        buf, _ = udp_unicast_socket.recvfrom(MAX_BUF_SIZE)
        nick, _, payload = buf.decode(ENCODING).partition(":")
        print(f"Message from {nick}: {payload}")


def handle_sending_udp_multicast(nick: str, udp_multicast_socket: socket.socket,
                                 multicast_address: str, multicast_port: int) -> None:
    udp_multicast_socket.sendto(
        bytes(f"{nick}:{ASCII_ART}", ENCODING), (multicast_address, multicast_port)
    )


def handle_receiving_udp_multicast(udp_multicast_socket: socket.socket, multicast_address: str,
                                   multicast_port: int) -> None:
    pass


def main() -> int:
    signal.signal(signal.SIGINT, signal_handler)

    multicast_address, multicast_port = sys.argv[1], int(sys.argv[2])

    nick = input("Your nick: ")
    udp_unicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

    client_handler = Thread(
        target=handle_client,
        args=(nick, udp_unicast_socket, udp_multicast_socket, multicast_address, multicast_port),
        daemon=True
    )
    udp_server_receiver = Thread(
        target=handle_receiving_udp_unicast,
        args=(udp_unicast_socket,),
        daemon=True
    )
    udp_multicast_receiver = Thread(
        target=handle_receiving_udp_multicast,
        args=(udp_multicast_socket, multicast_address, multicast_port),
        daemon=True
    )

    client_handler.start()
    udp_server_receiver.start()
    udp_multicast_receiver.start()

    client_handler.join()
    udp_server_receiver.join()
    udp_multicast_receiver.join()

    return 0


if __name__ == "__main__":
    main()
