"""
Interactive utility for sending commands to the command socket 

Prototype for the velouria-ctl command
"""

import socket
import readline

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect('/tmp/velouria.sock')

command = ''

while command != 'exit':
    command = raw_input("velouria> ")
    print command
    if command and command.lower() != 'exit':
        s.sendall(command+"\n")
        data = s.recv(1024)
        print data
        
        
s.close()
