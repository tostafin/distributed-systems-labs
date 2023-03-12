import socket
from threading import Thread

from constants import IP, PORT, MAX_BUF_SIZE, MESSAGE, ENCODING, INIT_MSG


def receive_data_from_server(client: socket.socket):
    buf: bytes
    try:
        while buf := client.recv(MAX_BUF_SIZE):
            nick, _, message = buf.decode(ENCODING).partition(":")
            print(f"Message from {nick}: {message}")

    except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    # create an INET, STREAMing socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # now connect to the localhost
        client_socket.connect((IP, PORT))
        try:
            nick = input("Your nick: ")
            client_socket.sendall(bytes(INIT_MSG, ENCODING))
            print("You're connected to the server. You can send and receive messages now.")
            server_data_receiver = Thread(target=receive_data_from_server, args=(client_socket,), daemon=True)
            server_data_receiver.start()
            while True:
                message = input()
                if len(message) <= MAX_BUF_SIZE:
                    client_socket.sendall(bytes(MESSAGE.format(nick=nick, message=message), ENCODING))
                else:
                    print(f"Message too long, maximum {MAX_BUF_SIZE} characters.")

        except KeyboardInterrupt:
            print("Client finished.")
