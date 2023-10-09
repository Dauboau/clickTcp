
import socket
import time

class ClientSocket:

    def __init__(self,host="localhost",port=54545):

        self.sock = socket.socket()
        self.sock.connect((host, port))

        print("Conectado ao inimigo como client!")

    def get_data(self):
        return self.sock.recv(1024)
    
class ServerSocket:

    def __init__(self,host="localhost",port=54546):

        self.serversocket = socket.socket()
        self.serversocket.bind(('', port))

        self.serversocket.listen(1)

        self.clientsocket,addr = self.serversocket.accept()

        print("Conectado ao inimigo como servidor!")

    def send_data(self,clicks):

        msg = str(clicks)
        self.clientsocket.send(msg.encode('ascii'))

        return