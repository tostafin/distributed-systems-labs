import socket
import signal
import sys

from threading import Thread

from constants import IP, PORT, MAX_BUF_SIZE, MESSAGE, ENCODING, INIT_MSG, UDP_UNICAST_MSG, ASCII_ART


udp_unicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def signal_handler(sig, frame):
    print("\nClient finished.")
    sys.exit(0)


def receive_data_from_server(client: socket.socket) -> None:
    buf: bytes
    while buf := client.recv(MAX_BUF_SIZE):
        nick, _, message = buf.decode(ENCODING).partition(":")
        print(f"Message from {nick}: {message}")


def handle_tcp_client(nick: str) -> None:
    # create an INET, STREAMing socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # now connect to the localhost
        client_socket.connect((IP, PORT))

        client_socket.sendall(bytes(INIT_MSG, ENCODING))
        handle_sending_udp_unicast(nick, True)
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
                handle_sending_udp_unicast(nick, False)
                continue
            if len(message) <= max_msg_len:
                client_socket.sendall(bytes(MESSAGE.format(
                    nick=nick, message=message), ENCODING))
            else:
                print(f"Message too long, maximum {max_msg_len} characters.")


def handle_sending_udp_unicast(nick: str, init: bool) -> None:
    if init:
        udp_unicast_socket.sendto(bytes(INIT_MSG, ENCODING), (IP, PORT))
    else:
        udp_unicast_socket.sendto(bytes(f"{nick}:{ASCII_ART}", ENCODING), (IP, PORT))


def handle_receiving_udp_unicast() -> None:
    while True:
        buf, _ = udp_unicast_socket.recvfrom(MAX_BUF_SIZE)
        nick, _, payload = buf.decode(ENCODING).partition(":")
        print(f"Message from {nick}: {payload}")


def main() -> int:
    signal.signal(signal.SIGINT, signal_handler)

    nick = input("Your nick: ")

    tcp_client_handler = Thread(target=handle_tcp_client, args=(nick,), daemon=True)
    udp_server_receiver = Thread(target=handle_receiving_udp_unicast, daemon=True)

    tcp_client_handler.start()
    udp_server_receiver.start()

    tcp_client_handler.join()
    udp_server_receiver.join()

    return 0


if __name__ == "__main__":
    main()
