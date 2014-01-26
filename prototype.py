"""
Basic WebKit Example
"""

from gi.repository import Gtk, WebKit, Gdk, GLib
import os, sys

class MyWindow(Gtk.Window):
    
    browsers = None
    
    in_fullscreen = False
    initial_cursor = None
    
    def relative_file_uri(self, path):
        """
        Take a path relative to *the current working directory* and make it absolute,
        format it into a proper URI
        """
        return "file://"+os.path.abspath(path)
    
    def add_browser(self, uri):
        browser = WebKit.WebView()
        browser.load_uri(uri)
        # prevent user interaction
        browser.set_sensitive(False)
        label = Gtk.Label(uri)
        
        self.notebook.append_page(browser, label)

    def on_realized(self, widget=None, event=None):
        # self.toggle_fullscreen()
        print "Realized"
        self.toggle_fullscreen()

    def __init__(self):
        self.browsers = []
        
        Gtk.Window.__init__(self, title="Hello World")
        
        self.set_default_size(400, 400)
        
        self.connect("key_press_event", self.key_dispatch)
        self.connect("realize", self.on_realized)
        # self.connect("motion-notify-event", self.hide_cursor)
        
        self.notebook = Gtk.Notebook()
        self.notebook.set_show_border(False)
        self.notebook.set_show_tabs(False)
        self.notebook.set_scrollable(False)
        self.notebook.popup_disable()
        
        self.add(self.notebook)
        
        self.add_browser(self.relative_file_uri("index.html"))
        self.add_browser(self.relative_file_uri("cube.jpg"))
        self.add_browser(self.relative_file_uri("full_of_fish.png"))
        self.add_browser("http://www.google.com")
        self.add_browser("http://www.flickr.com/photos/tags/ocean/show/")
        
        GLib.timeout_add_seconds(5, self.next_timeout)
        
        
        
        
    def _create_next_timeout(self):
        """
        Create a timeout to switch browsers
        """
        
    def next_timeout(self):
        """
        Calls self.next_browser(), then sets up a timeout to call itself again
        
        TODO: get the interval from some sort of data structure
        """
        self.next_browser()
        GLib.timeout_add_seconds(5, self.next_timeout)
        
    def next_browser(self):
        """
        Rotate to the next page
        """
        count = self.notebook.get_n_pages()
        
        current = self.notebook.get_current_page()
        
        next = current+1
        
        # if we're at the last browser, go to the first one
        if next >= count:
            next = 0
        
        self.notebook.set_current_page(next)

    def on_button_clicked(self, widget):
        print("Hello World")
        Gtk.main_quit()
        
        
    def track_fullscreen(self, widget, event):
        """
        Bind to the 'window-state-event' to set the fullscreen status of the 
        application.
        """
        import ipdb; ipdb.set_trace();
        
    def key_dispatch(self, widget, event):
        """
        Bound to 'key-press-event'; dispatches keypresses to various methods
        """
        # if you press CTRL-F
        if event.state == Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_f:
            self.toggle_fullscreen()
        if event.keyval == Gdk.KEY_n:
            self.next_browser()
        if event.keyval == Gdk.KEY_Escape:
            self.quit()
        
    def quit(self):
        """
        Exit the application
        """
        Gtk.main_quit()
        
    def hide_cursor(self):
        window = self.get_window()
        self.initial_cursor = window.get_cursor()
        print self.initial_cursor
        display = self.get_display()
        cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.BLANK_CURSOR)
        
        
        window.set_cursor(cursor)
        
    def show_cursor(self):
        window = self.get_window()
        window.set_cursor(self.initial_cursor)
        
    def toggle_fullscreen(self, event=None):
        """
        When the user presses CTRL-F, toggle the window from fullscreen to
        not-fullscreen.
        
        TODO: Ensure fullscreen is actually happened by monitoring the window-state-event 
              signal
        """
        if not self.in_fullscreen:
            self.hide_cursor()
            self.fullscreen()
            self.in_fullscreen = True
        else:
            self.show_cursor()
            self.unfullscreen()
            self.in_fullscreen = False
            
        

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

