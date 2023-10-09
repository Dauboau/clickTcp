
import socket
import time

class ClientSocket:

    def __init__(self,host="localhost",port=54545):

        self.sock = socket.socket()
        self.port = port
        self.host = host

    def connect(self):
        self.sock.connect((self.host, self.port))
        print("Conectado ao inimigo como client pela porta:",self.port)

    def get_data(self):
        return self.sock.recv(1024)
    
class HostSocket:

    def __init__(self,port=54546):

        self.sock = socket.socket()
        self.port=port

    def connect(self):
        self.sock.bind(('', self.port))
        self.sock.listen(1)
        self.sock,addr = self.sock.accept()
        print("Conectado ao inimigo como servidor pela porta:",self.port)

    def send_data(self,clicks):

        msg = str(clicks)
        self.sock.send(msg.encode('ascii'))

        return