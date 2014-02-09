"""
Client for the dispatch_server.py server.

Sends a few commands, prints the result.
"""

import socket

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect('/tmp/velouria.sock')

s.sendall('COUNT\n')
s.sendall('PREV\n')
s.sendall('HELLO\n')
s.sendall('NEXT\n')
s.sendall('PREV\n')
s.sendall('COUNT\n')

data = s.recv(1024)
s.close()
print 'Received', repr(data)
