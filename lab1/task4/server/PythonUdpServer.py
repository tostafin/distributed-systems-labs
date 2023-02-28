import socket

serverPort = 9008
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))
buff = []

print('PYTHON UDP SERVER')

while True:
    buff, address = serverSocket.recvfrom(1024)
    buff = str(buff, 'cp1250')
    if msg := buff.partition("JAVA: ")[2]:
        serverSocket.sendto(bytes("Pong Java", 'cp1250'), address)
    elif msg := buff.partition("PYTHON: ")[2]:
        serverSocket.sendto(bytes("Pong Python", 'cp1250'), address)
    else:
        raise ValueError("Wrong message structure; should be: <JAVA>/<PYTHON>: <message>")
