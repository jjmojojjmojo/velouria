"""
Basic echo server.

Uses a unix domain socket to communicate.

Based on http://docs.python.org/2/library/asyncore.html#asyncore-example-basic-echo-server
"""

import asyncore
import socket
import os

class EchoHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.send(data)

class EchoServer(asyncore.dispatcher):

    def __init__(self, socket_file="server.sock"):
        asyncore.dispatcher.__init__(self)
        if os.path.exists(socket_file):
            os.unlink(socket_file)
        
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(socket_file)
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection'
            handler = EchoHandler(sock)

server = EchoServer()
asyncore.loop()
