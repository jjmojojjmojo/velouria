"""
Velouria: Browser Slide
=======================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
Slide API implementation that uses a webkit browser widget to display a 
given URI.

TODO: find a way to always hide scrollbars
"""

from velouria.slide.common import Slide, VelouriaConfigSlide
from gi.repository import Gtk, WebKit2, Gdk

class VelouriaConfigBrowserSlide(VelouriaConfigSlide):
    """
    Data structure to set defaults for and hold values of [slide_name] entries
    in velouria.conf
    """
    _always_list = False
    
    _defaults = {
        'delay': '5',
        'data_directory': '',
        'uri': '',
    }
    
class BrowserSlide(Slide):
    """
    A slide that presents a web browser to the user.
    """
    _config = VelouriaConfigBrowserSlide
    
    widget = None
    
    def widget(self):
        browser = WebKit2.WebView()
        
        browser.load_uri(self.config.uri)
        # prevent user interaction
        browser.set_sensitive(False)
        browser.set_resize_mode(Gtk.ResizeMode.QUEUE)
        
        return browser
        
    def reload(self):
        print "RELOADING"
        self._show = False
        self._widget.reload_bypass_cache()
        
    
