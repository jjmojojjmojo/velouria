"""
Velouria: Entry Points
======================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application

This file contains entry points registered with the setuptools' console_scripts
mechanism.

Two CLI scripts are provided:
* velouria - the application itself
* velouria-ctl - convenience wrapper for sending signals to the 
                 main application.
"""

VERSION="0.1"
from app import Velouria
from controller import VelouriaServer, VelouriaController
import signal
import asyncore
from gi.repository import Gtk, GLib

def ctl():
    """
    Velouria-control entry point - sends signals to the main application
    to control it
    """
    VelouriaController()

def poll():
    """
    Wiring the poll function from asyncore to the main GTK loop
    """
    asyncore.poll(timeout = 0.0)
    GLib.timeout_add(250, poll)

def main():
    """
    Main entry into the application.
    
    TODO: support CLI options
    """
    app = Velouria()
    app.window.show_all()
    
    controller = VelouriaServer(app)
    
    # wire up the signal handlers
    signal.signal(signal.SIGINT, controller.shutdown)
    signal.signal(signal.SIGINT, app.shutdown)
    
    # main loops
    poll()
    Gtk.main()
