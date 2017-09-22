import socket
import asyncore
import time
import sys

REMOTE_HOST = 'localhost'
REMOTE_PORT = 8089
MAX_MSG_LEN = 65536

class BotHandler(asyncore.dispatcher):
    def __init__(self, sock, map, server):
        self.server = server
        self.buffer = ''
        asyncore.dispatcher.__init__(self, sock, map)

    def writable(self):
        return len(self.buffer) > 0

    def readable(self):
        return True

    def handle_read(self):
        """Notify server of any new incoming data"""
        data = self.recv(MAX_MSG_LEN)
        if data:
            print("Got some data: %s"%data.decode('utf-8'))

    def handle_write(self):
        """send some amount of buffer"""
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]

class IRISCommandCenter(asyncore.dispatcher):
    """Receive and forward chat messages

    When a new connection is made we spawn a dispatcher for that
    connection.
    """
    ADDRESS_FAMILY = socket.AF_INET
    SOCKET_TYPE = socket.SOCK_STREAM
    def __init__(self, host=REMOTE_HOST, port=REMOTE_PORT):
        self.map = {}
        self.address = (host,port)
        self.bots = []
        self.frontends = []
        asyncore.dispatcher.__init__(self, map=self.map)

    def start(self):
        """Bind to socket and start asynchronous loop"""
        self.create_socket(self.ADDRESS_FAMILY, self.SOCKET_TYPE)
        self.bind(self.address)
        self.listen(1)
        asyncore.loop(map=self.map)

    def writable(self):
        return False

    def readable(self):
        return True

    def newMessage(self, data, fromWho): #Communicate with all Bots
        """Put data in all clients' buffers"""
        for bot in self.bots:
            bot.buf = bot.buf + data

    def handle_accept(self):
        """Deal with newly accepted connection"""
        print('got new connection, waiting for init message')
        (connSock, clientAddress) = self.accept()
        

        timestamp = time.time()
        init_message_recieved = False
        while((time.time()-timestamp) < 5):
            buf = connSock.recv(MAX_MSG_LEN)
            if len(buf) > 0:
                print("Init message recieved: %s"%buf.decode('utf-8'))
                init_message_recieved = True
                break
        if init_message_recieved:
            self.bots.append(BotHandler(connSock, self.map, self))
        else:
            print("Connection did not supply valid init message within allowed timeframe")

    def stop(self):
        """ Attempt graceful shutdown """
        self.close()

server = IRISCommandCenter()
try:
    server.start()
except KeyboardInterrupt:
    print("Keyboard interupt detected, attempting graceful shutdown")
    server.stop()
    sys.exit()

#serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#serversocket.bind(('localhost', 8089))
#serversocket.listen(5) # become a server socket, maximum 5 connections

# while True:
#     connection, address = serversocket.accept()
#     buf = connection.recv(65536)
#     if len(buf) > 0:
#         print(buf.decode('utf-8'))p
