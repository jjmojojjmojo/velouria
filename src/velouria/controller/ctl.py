"""
Velouria: Controller
====================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
This module contains the core logic for the velouria-ctl command line tool.

TODO: what other useful commands or information could the server or this tool
      give us?
      
TODO: using server.VelouriaDispatcher as the single source of truth for supported
      commands - is this sound long-term?
"""

import argparse
import socket
import os, sys
import velouria.config
from server import VelouriaDispatcher, VelouriaHandler

import logging
logger = logging.getLogger("velouria")

class VelouriaController(object):
    
    config = None
    options = None
    parser = None
    logger = None
    
    def command(self, command):
        """
        Send a single command to the VelouriaServer instance, and return 
        the response.
        
        Opens and closes the connection upon each call. Multiple commands
        can be separated if needed by newlines (\n)
        
        TODO: make the error message when the socket file is not there (e.g.
              the Velouria app is not running) more user friendly.
        """
        self.logger.info(
            "RUNNING COMMAND %s, config file: %s", 
            command, 
            self.options.config_file
        )
        
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(self.config.main.socket_file)
        except socket.error, e:
            logging.error("ERROR: %s", e)
            sys.exit(1)
        
        s.sendall(command+"\n")
        
        output = ''
        
        while 1:
            response = s.recv(1024)
            output += response
            # the end of the data is marked by two linebreaks - but query
            # the class property to be sure
            if output.endswith(VelouriaHandler.end_transmission):
                break
            
        s.close()
        
        return output
        
    
    def __init__(self):
        """
        Run the command via argparse setup.
        
        TODO: add command option for specifying the socket file directly?
        TODO: should this be moved to another method? possibly __call__ ?
        """
        self.parser = argparse.ArgumentParser(
            description='Control a running Velouria instance.',
        )
        
        self.parser.add_argument(
            "command", 
            choices=VelouriaDispatcher.actions,
            metavar="COMMAND",
            help="A command to send to velouria. Any output will be returned to STDOUT",
        )
        
        velouria.config.common_args(self.parser)
        
        self.options = self.parser.parse_args()
        
        self.logger = velouria.config.setup_logging(self.options.log_level, self.options.log_file)
        
        self.config = velouria.config.VelouriaConfig(self.options.config_file)
        print self.command(self.options.command)
