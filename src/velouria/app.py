"""
Velouria: Primary Application
=============================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
This module contains classes that are invoked as part of running the Velouria
application.
"""
from gi.repository import Gtk, Gdk, GLib

from config import VelouriaConfig, setup_logging
from slide import Slide

import logging, datetime

class Velouria(object):
    """
    Primary controller for the application.
    """
    
    config = None
    slides = None
    config_file = None
    _initial_cursor = None
    
    fullscreen = False
    
    window = None
    
    paused = False
    current = 0
    logger = None
    
    # last time the reload method was called
    reloaded = None
    
    def set_style(self):
        self.logger.info("Setting GDK Screen style")
        screen = Gdk.Screen.get_default()
        if screen:
            Gtk.StyleContext.add_provider_for_screen(screen, self.config.style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        else:
            self.logger.debug("No default screen")
    
    def __init__(self, config):
        self.logger = logging.getLogger("velouria")
        
        self.config = config
        
        self.set_style()
        
        self.window = Gtk.Window(title=self.config.main.title)
        
        self.window.set_default_size(self.config.main.width, self.config.main.height)
        
        self.window.connect("key-press-event", self.on_keypress_dispatch)
        self.window.connect("realize", self.on_realize)
        self.window.connect("window-state-event", self.on_window_state_change)
        
        self.notebook = Gtk.Notebook()
        self.notebook.set_show_border(False)
        self.notebook.set_show_tabs(False)
        self.notebook.set_resize_mode(Gtk.ResizeMode.QUEUE)
        
        self.window.add(self.notebook)
        
        self.slides = []
        
        for slide, type_, class_ in self.config.slides:
            slide_obj = class_(slide, self)
            self.slides.append(slide_obj)
            slide_obj.widget.set_sensitive(False)
            self.notebook.add(slide_obj.widget)
        
        self.window.connect("delete-event", Gtk.main_quit)
        
        if self.config.main.paused_on_start:
            self.paused = True
        
        self.rotation()
        
        self.window.show_all()
        
    def on_window_state_change(self, widget, event):
        """
        Track the fullscreen/not fullscreen state of the window
        """
        
        if event.changed_mask == Gdk.WindowState.FULLSCREEN:
            self.logger.debug("FULLSCREEN DETECTED")
            if self.fullscreen:
                self.fullscreen = False
            else:
                self.fullscreen = True
    
    def _keypress_action(self, event):
        """
        Given an event, return the action to take based on the
        self.config.keyboard settings
        """
        self.logger.debug("KEYVAL: %s STATE: %s", event.keyval, event.state)
        print "KEYVAL: %s STATE: %s" % (event.keyval, event.state)
        
        
        for action, mappings in self.config.keyboard:
             for mapping in mappings:
                self.logger.debug("ACTION: %s KEY: %s MODIFIERS: %s", action, mapping['key'], mapping['modifiers'])
                print "ACTION: %s KEY: %s MODIFIERS: %s" % (action, mapping['key'], mapping['modifiers'])
                if mapping['key'] == event.keyval and event.state == mapping['modifiers']:
                    return action
                    
        self.logger.debug("NO MAPPING FOUND")
        print "NO MAPPING FOUND"
    
    def keypress_dispatch(self, action):
        self.logger.info("ACTION: %s", action)
        
        if action == 'fullscreen':
            self.toggle_fullscreen()
        if action in ('forward', 'next'):
            self.next()
        if action == 'back':
            self.back()
        if action == 'quit':
            self.quit()
        if action == 'pause':
            self.toggle_pause()
        if action == 'reload':
            self.reload()
    
    def on_keypress_dispatch(self, widget, event):
        """
        Dispatch keypress events to various methods
        
        TODO: use keyboard config to drive
        """
        self.logger.debug("KEYPRESS EVENT: %s, %s", event.state, event.keyval)
        
        action = self._keypress_action(event)
        
        self.keypress_dispatch(action)
    
    def on_realize(self, widget):
        if self.config.main.fullscreen_on_start:
            self.toggle_fullscreen()
        else:
            self.logger.debug("Full screen on start is turned OFF")
    
    def hide_cursor(self):
        self.logger.debug("Hiding cursor")
        
        window = self.window.get_window()
        self._initial_cursor = window.get_cursor()
        
        display = self.window.get_display()
        cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.BLANK_CURSOR)
        window.set_cursor(cursor)
        
    def show_cursor(self):
        self.logger.debug("Showing cursor")
        
        window = self.window.get_window()
        window.set_cursor(self._initial_cursor)
        
    def toggle_fullscreen(self, event=None):
        """
        When the user presses CTRL-F (remappable), toggle the window from fullscreen to
        not-fullscreen.
        """
        print "CALLED, state: %s" % (self.fullscreen)
        if not self.fullscreen:
            self.hide_cursor()
            self.window.fullscreen()
        else:
            self.show_cursor()
            self.window.unfullscreen()
            
    def toggle_pause(self):
        """
        Pause/Unpause rotation
        """
        if self.paused:
            self.paused = False
            self.rotation()
        else:
            self.paused = True
    
    
    def quit(self):
        """
        Exit the application
        """
        self.logger.debug("Quitting main GTK loop...")
        Gtk.main_quit()
        
    def shutdown(self, signal, frame):
        """
        Signal handler for SIGINT
        """
        self.logger.info("Shutting down...")
        self.quit()
        
    def next(self):
        """
        Display the next slide
        """
        count = len(self.slides)
        
        next = self.current+1
        
        if next >= count:
            next = 0
                
        self.notebook.set_current_page(next)
        self.current = next
        
    def back(self):
        """
        Display the previous slide
        """
        count = len(self.slides)
        
        next = self.current-1
        
        if next < 0:
            next = count-1
        
        self.notebook.set_current_page(next)
        self.current = next
        
    def rotate(self):
        """
        Go next and then re-run rotation
        """
        if self.paused:
            return False
        
        self.next()
        self.rotation()
        
    def rotation(self):
        """
        Begin rotating the pages in self.notebook (cycle through the slides)
        
        Figures out the delay based on the configuration for the current slide.
        """
        delay = self.slides[self.current].config.delay
        GLib.timeout_add_seconds(delay, self.rotate)
        
    def reload(self):
        """
        Call the reload() method of each slide
        """
        self.reloaded = datetime.datetime.now()
        for slide in self.slides:
            slide.reload()
            
