"""
Velouria: Primary Application
=============================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
This module contains classes used to receive signals via a unix domain socket
to control the main application.

TODO: consider using a singleton instead of passing the application object around
      in constructors.
"""

import asyncore, asynchat
import socket
import os
import signal
import logging

class VelouriaDispatcher(object):
    """
    Callable that maps commands sent over 'the wire' to actions in the main 
    Velouria app.
    
    Currently just proxies for Velouria.on_keypress_dispatch, but has some
    error handling built in for uninitiated clients.
    """
    
    actions = (
        'fullscreen',
        'forward',
        'next',
        'back',
        'quit',
        'pause',
        'reload'
    )
    
    velouria = None
    logger = None
    
    def __init__(self, velouria):
        """
        velouria is a running Velouria application object
        """
        self.velouria = velouria
        self.logger = logging.getLogger("velouria")
    
    def __call__(self, command):
        command = command.lower()
        
        self.logger.debug("Dispatching command: %s", command)
        
        output = ""
        
        if command in self.actions:
            try:
                self.velouria.keypress_dispatch(command)
                output = "'%s' command executed successfully" % (command)
            except Exception, e:
                # if anything goes wrong, report back to the client what the 
                # exception was
                output = "ERROR: %s raised when executing command '%s': %s" % (e.__class__, command, e)
        else:
            output = "ERROR: '%s' is not a supported command" % (command)
            
        self.logger.debug(output)
        
        return output

class VelouriaHandler(asynchat.async_chat):
    """
    Simple newline-terminated receiver. 
    
    Send commands like "fullscreen" or "pause" (maps to the actions in the
    Dispatcher class above) to on_keypress_dispatch in the main 
    application
    """
    buffer = ''
    velouria = None
    end_transmission = "\n\n"
    
    def __init__(self, sock, velouria):
        asynchat.async_chat.__init__(self, sock=sock)
        self.set_terminator("\n")
        
        self.velouria = velouria
        
        self.dispatcher = VelouriaDispatcher(velouria)
        
        
        
    def collect_incoming_data(self, data):
        self.buffer += data
        
    def found_terminator(self):
        """
        Proxy the command to the dispatcher, send the returned output
        back to the client.
        """
        output = self.dispatcher(self.buffer)
        self.push(output+self.end_transmission)
        self.buffer = ''

class VelouriaServer(asyncore.dispatcher):
    
    velouria = None
    
    def __init__(self, velouria):
        self.logger = logging.getLogger("velouria")
        
        self.logger.info("Initializing command server...")
        asyncore.dispatcher.__init__(self)
        
        self.velouria = velouria
        
        socket_file = self.velouria.config.main.socket_file
        
        if os.path.exists(socket_file):
            self.logger.info("Removing stale socket file %s", socket_file)
            os.unlink(socket_file)
        
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(socket_file)
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            self.logger.debug('Incoming command connection: %s', pair)
            handler = VelouriaHandler(sock, self.velouria)
            
    def shutdown(self, signal, frame):
        """
        Called by signal when someone hits control-c (sends SIGINT)
        """
        self.logger.info("Shutting down command server...")
        self.close()
