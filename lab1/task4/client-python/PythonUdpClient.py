import socket

serverIP = "127.0.0.1"
serverPort = 9008
msg = "PYTHON: Ping"

print('PYTHON UDP CLIENT')
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(bytes(msg, 'utf8'), (serverIP, serverPort))

buff, address = client.recvfrom(1024)
print("received msg: " + str(buff, 'cp1250'))
