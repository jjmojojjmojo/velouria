"""
Velouria: Slide Classes
=======================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
This module contains classes that display information in the Velouria 
application
"""

from gi.repository import Gtk, GdkPixbuf
import os, sys
from common import Slide
from browser import BrowserSlide
from scaled_image import ScaledImageSlide
