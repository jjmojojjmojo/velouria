"""
Velouria: Controller
====================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
This module contains classes used to receive signals via a unix domain socket
to control the main application.

It has two parts: 
    - server.py: the server that runs with the main GTK loop waiting for commands
    - ctl.py: the CLI application that allows the user to send commands
"""
from server import VelouriaServer
from ctl import VelouriaController