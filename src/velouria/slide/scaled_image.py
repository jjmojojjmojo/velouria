"""
"""
from gi.repository import Gtk, GdkPixbuf
from common import VelouriaConfigSlide, Slide

import os

class VelouriaConfigScaledImage(VelouriaConfigSlide):
    """
    Data structure to set defaults for and hold values of [slide_name] entries
    in velouria.conf
    """
    _defaults = {
        'delay': '5',
        'data_directory': '',
        'image': '',
        'apsect': ''
    }
    _always_list = False
    
    def process_option(self, name, value):
        if name == 'data_directory':
            # current working directory if not specified
            return os.path.abspath(value)
        else:
            return super(VelouriaConfigScaledImage, self).process_option(name, value)

class ScaledImageSlide(Slide):
    """
    Slide that displays a single scaled image.
    """
    name = None
    
    # the configuration class to use
    _config = VelouriaConfigScaledImage
    
    # reference to our widget
    widget = None
    
    # pixbuf of our image
    _image = None
    
    # our image widget
    _image_widget = None
    
    # reference to our parent Velouria app
    velouria = None
    
    def widget(self):
        """
        Return the widget for this slide
        """
        if self.config.image:
            if not os.path.isabs(self.config.image):
                path = os.path.join(self.config.data_directory, self.config.image)
            else:
                path = self.config.image
        else:
            path = os.path.join(os.path.dirname(__file__), "cube.jpg")
        
        container = Gtk.Box.new(False, 0)
        
        self._image_widget = Gtk.Image.new()
        self._image = GdkPixbuf.Pixbuf.new_from_file(path)
        
        self.velouria.window.connect('configure-event', self.on_window_state_event)

        container.pack_start(self._image_widget, False, False, 0)
        container.set_resize_mode(Gtk.ResizeMode.QUEUE)
        
        return container
    
    def on_window_state_event(self, widget, event):
        window = widget.get_window()
        
        x, y, width, height = window.get_geometry()
        
        self._reload_image(width, height)
        
    
    def _reload_image(self, width, height):
        print "WIDTH: %s HEIGHT: %s" % (width, height)
        buff = self._image.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
        self._image_widget.set_from_pixbuf(buff)
    
    def reload(self):
        """
        Called when the main application wants us to refresh ourselves.
        """
