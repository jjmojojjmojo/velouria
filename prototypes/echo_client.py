"""
Sends data to the echo_server.py server, and prints what is returned.

See: http://docs.python.org/2/library/socket.html#example
"""
import socket

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect('server.sock')

s.sendall('Hello, world')

data = s.recv(1024)
s.close()
print 'Received', repr(data)
