"""
Velouria: Slide Classes
=======================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
This module contains classes that display information in the Velouria 
application
"""

from gi.repository import Gtk, GdkPixbuf
import cairo
import os, sys
from velouria.config import VelouriaConfigSection
from velouria.exceptions import ConfigValueError
from velouria import VERSION

class VelouriaConfigSlide(VelouriaConfigSection):
    """
    Data structure to set defaults for and hold values of [slide_name] entries
    in velouria.conf
    """
    _defaults = {
        'delay': '5',
    }
    
    def process_option(self, name, value):
        if name in ('delay'):
            try:
                val =  int(value)
                if val < 0:
                    raise ValueError
                return val
            except ValueError:
                raise ConfigValueError, "'%s' is not a valid delay" % (value, name)
        else:
            return super(VelouriaConfigSlide, self).process_option(name, value)


class Slide(object):
    """
    Base class for all slides - just shows a single, hard-coded image.
    """
    
    name = None
    
    # the configuration class to use
    _config = VelouriaConfigSlide
    
    # our config object
    config = None
    
    # reference to our widget
    widget = None
    
    # reference to our parent Velouria app
    velouria = None
    
    def __init__(self, name, parent):
        """
        Constructor - pass a unique name and the parent Velouria object
        """
        self.name = name
        self.config = self._config(parent.config.config, name)
        
        self.velouria = parent
        self.widget = self.widget()

    
    def widget(self):
        """
        Return the widget for this slide. This is where you can hook into 
        signal handlers.
        """
        container = Gtk.HBox()
        
        label = Gtk.Label("Velouria version %s" % VERSION)
        
        container.pack_start(label, True, True, 0)
        
        return container
    
    def reload(self):
        """
        Called when the main application wants us to refresh ourselves.
        """
