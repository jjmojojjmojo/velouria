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
from gi.repository import Gtk

def ctl():
    """
    Velouria-control entry point - sends signals to the main application
    to control it
    """
    

def main():
    """
    Main entry into the application.
    
    TODO: support CLI options
    """
    app = Velouria()
    app.window.show_all()
    Gtk.main()
