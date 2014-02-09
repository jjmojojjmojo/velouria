"""
Velouria: Primary Application
=============================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
This module contains classes that are invoked as part of running the Velouria
application.
"""
from gi.repository import Gtk, Gdk, GLib

from config import VelouriaConfig
from slide import Slide

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
    
    def set_style(self):
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, self.config.style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    def __init__(self, config_file=None):
        self.config_file = config_file
        
        self.config = VelouriaConfig(self.config_file)
        
        self.set_style()
        
        self.window = Gtk.Window(title=self.config.main.title)
        
        self.window.set_default_size(self.config.main.width, self.config.main.height)
        
        self.window.connect("key_press_event", self.on_keypress_dispatch)
        
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
        
    def on_window_state_change(self, widget, event):
        """
        Track the fullscreen/not fullscreen state of the window
        """
        print event.changed_mask
        if event.changed_mask == Gdk.WindowState.FULLSCREEN:
            if self.fullscreen:
                self.fullscreen = False
            else:
                self.fullscreen = True
    
    def _keypress_action(self, event):
        """
        Given an event, return the action to take based on the
        self.config.keyboard settings
        """
        for action, mappings in self.config.keyboard:
            print action+": ",
            for mapping in mappings:
                print mapping['key'],
                print mapping['modifiers']
                if mapping['key'] == event.keyval and event.state == mapping['modifiers']:
                    return action
    
    def keypress_dispatch(self, action):
        print "ACTION: %s" % (action)
        
        if action == 'fullscreen':
            self.toggle_fullscreen()
        if action == 'forward':
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
        print "KEYPRESS EVENT:"
        print "%s, %s" % (event.state, event.keyval)
        
        print "-----------"
        action = self._keypress_action(event)
        
        self.keypress_dispatch(action)
    
    def on_realize(self, widget):
        if self.config.main.fullscreen_on_start:
            self.toggle_fullscreen()
    
    def hide_cursor(self):
        window = self.window.get_window()
        self._initial_cursor = window.get_cursor()
        
        display = self.window.get_display()
        cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.BLANK_CURSOR)
        window.set_cursor(cursor)
        
    def show_cursor(self):
        window = self.window.get_window()
        window.set_cursor(self._initial_cursor)
        
    def toggle_fullscreen(self, event=None):
        """
        When the user presses CTRL-F (remappable), toggle the window from fullscreen to
        not-fullscreen.
        """
        print self.fullscreen
        
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
        Gtk.main_quit()
        
    def shutdown(self, signal, frame):
        """
        Signal handler for SIGINT
        """
        print "Shutting down..."
        self.quit()
        
    def next(self):
        """
        Display the next slide
        """
        count = len(self.slides)
        
        next = self.current+1
        
        if next >= count:
            next = 0
                
        
        print next
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
        
        print next
        self.notebook.set_current_page(next)
        self.current = next
        
    def rotate(self):
        """
        Go next and then 
        """
        if self.paused:
            return False
        
        self.next()
        self.rotation()
        
    def rotation(self):
        """
        Begin rotating the pages in self.notebook (cycle through the slides)
        """
        
        delay = self.slides[self.current].config.delay
        GLib.timeout_add_seconds(delay, self.rotate)
        
    def reload(self):
        """
        Call the reload() method of each slide
        """
        for slide in self.slides:
            slide.reload()
            
