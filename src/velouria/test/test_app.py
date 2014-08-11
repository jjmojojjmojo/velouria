"""
Velouria: Main Application Unit Tests
=====================================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
"""

from unittest import TestCase
from mock import MagicMock

class TestAppClass(TestCase):
    """
    Test the main Velouria class
    """
    
    def setUp(self):
        from velouria.config import VelouriaConfig
        import ConfigParser
        from velouria.app import Velouria
        
        # add 3 default slides to test interaction
        config = ConfigParser.ConfigParser()
        config.add_section("main")
        config.set('main', 'slides', 'slide1, slide2, slide3')
        
        for slide in ('slide1', 'slide2', 'slide3'):
            config.add_section(slide)
            config.set(slide, 'type', 'test')
            config.set(slide, 'delay', '2')
        
        # turn off rotation
        config.set('main', 'paused_on_start', 'on')
        
        vconfig = VelouriaConfig(config_object=config)
        
        app = Velouria(vconfig)
        
        self.advance()
        
        self._app = app
    
    def tearDown(self):
        del self._app
    
    def advance(self, delay=0):
        """
        Advances the GTK main loop.
        
        Adapted from: http://unpythonic.blogspot.ca/2007/03/unit-testing-pygtk.html
        """
        from gi.repository import Gtk
        import time
        import pprint
        
        
        # time.sleep(delay)
        # Gtk.main_iteration()
        
        print "events pending?! %s" % Gtk.events_pending()
        while Gtk.events_pending():
             Gtk.main_iteration_do(False)
             time.sleep(delay)
    
    def test_window_state_change(self):
        """
        Fullscreen should be set to true with default config.
        """
        from gi.repository import Gdk 
        app = self._app
        
        widget = MagicMock(name="widget")
        event = MagicMock(name="event")
        event.changed_mask = Gdk.WindowState.FULLSCREEN
        
        app.on_window_state_change(widget, event)
        
        self.advance(0.5)
        
        self.assertEquals(app.fullscreen, False)
        
        app.on_window_state_change(widget, event)
        
        self.advance(0.5)
        
        self.assertEquals(app.fullscreen, True)
        
    def test_on_realize(self):
        """
        Fullscreen is true on default object.on_realize()
        """
        app = self._app
        self.assertEquals(app.fullscreen, True)
        
        
    def _keypress(self, app, action, index=0):
        """
        For a given action and application object, simulate a keypress event
        
        app = Velouria application object
        action = the keyboard action to take (see 
                 Velouria.config.VelouriaConfigKeyboard for possible actions)
        index = keys can have multiple mappings, which one are you testing?
        """
        from gi.repository import Gdk 
        
        event = Gdk.EventKey()
        
        event.keyval = app.config.keyboard[action][index]['key']
        event.state = app.config.keyboard[action][index]['modifiers']
        
        import pprint
        pprint.pprint(app.config.keyboard[action])

        # doesn't actually seem to fire the event
        # app.window.do_key_press_event(app.window, event)
        
        app.on_keypress_dispatch(app.window, event)
        
        self.advance(0.5)
        
    def test_fullscreen_keypress(self):
        """
        Test that the default 'fullscreen' keybinding works.
        """
        
        app = self._app
        print "Initial: ",app.fullscreen
        self._keypress(app, 'fullscreen')
        
        self.advance(0.5)
        
        # with default config, fullscreen is set to true on init
        self.assertEquals(app.fullscreen, False)
        
        # it's been toggled off, now a keypress should turn it back on
        self._keypress(app, 'fullscreen')
        
        self.advance(0.5)
        
        self.assertEquals(app.fullscreen, True)
        
    def test_forward_keypress(self):
        """
        Test that the default 'forward' keybinding works.
        """
        app = self._app
        
        self._keypress(app, 'forward')
        
        self.assertEquals(app.current, 1)
        
        self._keypress(app, 'forward')
        
        self.assertEquals(app.current, 2)
        
        self._keypress(app, 'forward')
        
        self.assertEquals(app.current, 0)
        
    def test_back_keypress(self):
        """
        Test that the default 'back' keybinding works.
        """
        app = self._app
        
        self._keypress(app, 'back')
        
        self.assertEquals(app.current, 2)
        
        self._keypress(app, 'back')
        
        self.assertEquals(app.current, 1)
        
        self._keypress(app, 'back')
        
        self.assertEquals(app.current, 0)
        
    def test_reload_keypress(self):
        """
        Test that the default 'reload' keybinding works.
        """
        app = self._app
        
        self._keypress(app, 'reload')
        
        # timestamp of last reload gets set by the app when the event is
        # fired.
        self.assertNotEquals(app.reloaded, None)
        
    def test_pause_keypress(self):
        """
        Test that the default "pause" keybinding works.
        """
        app = self._app
        
        self._keypress(app, 'pause')
        
        # paused on startup, so now it should be off
        self.assertEquals(app.paused, False)
        
    def test_rotation(self):
        """
        Test rotating through each slide using the timeout
        """
        app = self._app
        
        app.toggle_pause()
        
        self.advance(1)
        
        self.assertEquals(app.current, 0)
        
        self.advance(1)
        
        self.assertEquals(app.current, 1)
        
        self.advance(1)
        
        self.assertEquals(app.current, 2)
        
        self.advance(1)
        
        self.assertEquals(app.current, 0)
