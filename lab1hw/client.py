import socket
import signal
import sys
import struct

from threading import Thread

from constants import (
    IP, PORT, MAX_BUF_SIZE, MESSAGE, ENCODING, INIT_MSG, UDP_UNICAST_MSG, UDP_MULTICAST_MSG,
    ASCII_ART
)


def signal_handler(sig, frame):
    print("\nClient finished.")
    sys.exit(0)


def set_up_client(nick: str, multicast_address: str, multicast_port: int) -> None:
    # create sockets
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((IP, PORT))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_unicast_socket:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as\
                    udp_multicast_socket:
                # send INIT messages
                send_tcp_message(client_socket, nick, INIT_MSG, True)
                send_udp_message_to_server(nick, udp_unicast_socket, True)
                print(
                    """You're connected to the server. You can now send and receive messages.
                    - Type U to send a UDP datagram with an ASCII Art.
                    - Type M to send a UDP multicast datagram with an ASCII Art.
                    """
                )

                # setup receivers
                tcp_message_receiver = Thread(
                    target=receive_tcp_message_from_server,
                    args=(client_socket,),
                    daemon=True
                )
                udp_server_receiver = Thread(
                    target=receive_udp_message_from_server,
                    args=(udp_unicast_socket,),
                    daemon=True
                )
                udp_multicast_receiver = Thread(
                    target=receive_udp_multicast_message,
                    args=(nick, udp_multicast_socket, multicast_address, multicast_port),
                    daemon=True
                )

                tcp_message_receiver.start()
                udp_server_receiver.start()
                udp_multicast_receiver.start()

                # message input and sending
                max_msg_len = MAX_BUF_SIZE - len(nick) - 1
                while True:
                    message = input()
                    if len(message) > max_msg_len:
                        print(f"Message too long, maximum {max_msg_len} characters.")
                    elif message == INIT_MSG:
                        print("This message is reserved for initializing.")
                    elif message == UDP_UNICAST_MSG:
                        send_udp_message_to_server(nick, udp_unicast_socket, False)
                    elif message == UDP_MULTICAST_MSG:
                        send_udp_multicast_message(
                            nick, udp_multicast_socket, multicast_address, multicast_port
                        )
                    else:
                        send_tcp_message(client_socket, nick, message, False)


def send_tcp_message(client_socket: socket.socket, nick: str, message: str, init: bool) -> None:
    if init:
        client_socket.sendall(bytes(INIT_MSG, ENCODING))
    else:
        client_socket.sendall(bytes(MESSAGE.format(nick=nick, message=message), ENCODING))


def receive_tcp_message_from_server(client: socket.socket) -> None:
    buf: bytes
    while buf := client.recv(MAX_BUF_SIZE):
        sender_nick, _, message = buf.decode(ENCODING).partition(":")
        print(f"Message from {sender_nick}: {message}")


def send_udp_message_to_server(nick: str, udp_unicast_socket: socket.socket, init: bool) -> None:
    if init:
        udp_unicast_socket.sendto(bytes(INIT_MSG, ENCODING), (IP, PORT))
    else:
        udp_unicast_socket.sendto(bytes(f"{nick}:{ASCII_ART}", ENCODING), (IP, PORT))


def receive_udp_message_from_server(udp_unicast_socket: socket.socket) -> None:
    while True:
        buf, _ = udp_unicast_socket.recvfrom(MAX_BUF_SIZE)
        sender_nick, _, payload = buf.decode(ENCODING).partition(":")
        print(f"Message from {sender_nick}: {payload}")


def send_udp_multicast_message(nick: str, udp_multicast_socket: socket.socket,
                               multicast_address: str, multicast_port: int) -> None:
    udp_multicast_socket.sendto(
        bytes(f"{nick}:{ASCII_ART}", ENCODING), (multicast_address, multicast_port)
    )


def receive_udp_multicast_message(nick: str, udp_multicast_socket: socket.socket,
                                  multicast_address: str, multicast_port: int) -> None:
    udp_multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_multicast_socket.bind((multicast_address, multicast_port))

    mreq = struct.pack("4sl", socket.inet_aton(multicast_address), socket.INADDR_ANY)

    udp_multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        buf, _ = udp_multicast_socket.recvfrom(MAX_BUF_SIZE)
        sender_nick, _, payload = buf.decode(ENCODING).partition(":")
        if sender_nick != nick:
            print(f"Message from {sender_nick}: {payload}")


def main() -> int:
    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} <multicast_address> <multicast_port>")
        sys.exit(0)

    multicast_address, multicast_port = sys.argv[1], int(sys.argv[2])

    nick = input("Your nick: ")

    set_up_client(nick, multicast_address, multicast_port)

    return 0


if __name__ == "__main__":
    main()
