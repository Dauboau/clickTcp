
import random
import socket
import string
import time


serversocket = socket.socket()

host = 'localhost'
port = 54545


serversocket.bind(('', port))

serversocket.listen(1)

clientsocket,addr = serversocket.accept()

print("got a connection from %s" % str(addr))

while True:
    time.sleep(1)
    msg = str(1)
    clientsocket.send(msg.encode('ascii'))
