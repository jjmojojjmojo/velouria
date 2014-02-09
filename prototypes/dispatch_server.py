"""
Command server - recieves simple string commands (newline terminated), dispatches
to a callable, and then returns the output of the callable to the client.
"""

import asyncore, asynchat
import socket
import os
import signal

class Dispatcher(object):
    """
    Simple callable that takes one argument, a command to dispatch.
    
    Attempts to call the function do_[command] on the current object.
    
    TODO: provide more complex calls - encode JSON or other structured data
          as part of the command.
    """
    
    count = 0
    
    def __call__(self, command):
        func = getattr(self, "do_%s" % (command.lower()), None)
        
        if not func:
            return "ERROR: Unkown command '%s'" % (command)
        else:
            return func()

    def do_hello(self):
        return "Well, hello yourself!"
        
    def do_count(self):
        msg = "CALLED %s TIMES" % (self.count)
        self.count += 1
        return msg

class Handler(asynchat.async_chat):
    
    buffer = ''
    
    def __init__(self, sock, dispatcher=None):
        asynchat.async_chat.__init__(self, sock=sock)
        self.set_terminator("\n")
        if not dispatcher:
            self.dispatcher = Dispatcher()
        else:
            self.dispatcher = dispatcher
        
    def collect_incoming_data(self, data):
        self.buffer += data
        
    def found_terminator(self):
        output = self.dispatcher(self.buffer)
        self.push(output+"\n\n")
        self.buffer = ''

class Server(asyncore.dispatcher):

    def __init__(self, socket_file="server.sock"):
        asyncore.dispatcher.__init__(self)
        
        if os.path.exists(socket_file):
            os.unlink(socket_file)
        
        self.dispatcher = Dispatcher()
        
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(socket_file)
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection'
            handler = Handler(sock, self.dispatcher)
            
    def shutdown(self, signal, frame):
        """
        Called by signal when someone hits control-c (sends SIGINT)
        """
        self.close()



server = Server()

# register the shutdown signal to the server object
signal.signal(signal.SIGINT, server.shutdown)

asyncore.loop()
