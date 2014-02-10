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
import pkg_resources

VERSION=pkg_resources.get_distribution("velouria").version

from app import Velouria
import exceptions
from controller import VelouriaServer, VelouriaController
import signal
import asyncore
from gi.repository import Gtk, GLib
from config import VelouriaConfig, setup_logging, common_args

import sys

import argparse

import logging

# set egg-wide default of INFO level, with output going to STDOUT
logger = setup_logging('info', 'STDOUT')

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
    
    TODO: factor this out to a class, like VelouriaController
    """
    logger = logging.getLogger("velouria")
    
    parser = argparse.ArgumentParser(
        description='Velouria: a plugable, configurable, resource-conservative'
                    'information kiosk application',
    )
    
    common_args(parser)
    
    options = parser.parse_args()
    try:
        config = VelouriaConfig(options.config_file)
        
        log_level = options.log_level
        log_file = options.log_file
        
        if not options.log_level:
            log_level = config.main.log_level
        if not log_file:
            log_file = config.main.log_file
        
        logger = setup_logging(log_level, log_file)
        
        logger.info("Starting Velouria v. %s...", VERSION)
    
        app = Velouria(config)
        app.window.show_all()
        
        controller = VelouriaServer(app)
        
        logger.debug("Registering signal handlers")
        # wire up the signal handlers
        signal.signal(signal.SIGINT, controller.shutdown)
        signal.signal(signal.SIGINT, app.shutdown)
        
        # main loops
        logger.debug("Running asyncore.poll, attaching timeout")
        poll()
        logger.debug("Starting main GTK loop")
        Gtk.main()
    except RuntimeError:
        logger.error("X not running or does not allow connections. Check $DISPLAY variable")
    except exceptions.ConfigError, e:
        logger.error("Configuration problem: '%s'", e)
