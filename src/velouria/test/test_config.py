"""
Velouria: Configuration Unit Tests
==================================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
"""

from unittest import TestCase

class TestCoeraseBoolean(TestCase):
    """
    Tests for the velouria.config.coerse_boolean function
    """
    
    def test_true(self):
        """
        Test typical usage, True values
        """
        from velouria.config import coerse_boolean
        
        self.assertTrue(coerse_boolean('True'))
        self.assertTrue(coerse_boolean('Yes'))
        self.assertTrue(coerse_boolean('T'))
        self.assertTrue(coerse_boolean('Y'))
        self.assertTrue(coerse_boolean('100'))
        self.assertTrue(coerse_boolean('on'))
    
    def test_false(self):
        """
        Test typical usage, False values
        """
        from velouria.config import coerse_boolean
        
        self.assertFalse(coerse_boolean('False'))
        self.assertFalse(coerse_boolean('F'))
        self.assertFalse(coerse_boolean('No'))
        self.assertFalse(coerse_boolean('N'))
        self.assertFalse(coerse_boolean('0'))
        self.assertFalse(coerse_boolean('off'))
        
    def test_none(self):
        """
        Test typical usage, None values
        """
        from velouria.config import coerse_boolean
        self.assertEquals(coerse_boolean(''), None)
        self.assertEquals(coerse_boolean(' '), None)
        self.assertEquals(coerse_boolean('\n     \t \n'), None)
        
    def test_exception(self):
        """
        Ensure that typical bad values raise ConfigValueError
        """
        from velouria.config import coerse_boolean
        from velouria.exceptions import ConfigValueError
        
        self.assertRaises(ConfigValueError, coerse_boolean, "-1")
        self.assertRaises(ConfigValueError, coerse_boolean, "hello")
        self.assertRaises(ConfigValueError, coerse_boolean, "s")
        
        
class TestParseKeyMapping(TestCase):
    """
    Test velouria.config.parse_key_mapping
    """
    
    def test_typical(self):
        """
        Test typical successful use
        """
        from velouria.config import parse_keymapping
        from gi.repository import Gdk
        
        expected = {
            'key': Gdk.KEY_space,
            'modifiers': 0,
        }
        
        self.assertEqual(expected, parse_keymapping('KEY_space'))
        
    def test_single_modifier(self):
        """
        Test use of a single modifier
        """
        from velouria.config import parse_keymapping
        from gi.repository import Gdk
        
        expected = {
            'key': Gdk.KEY_q,
            'modifiers': Gdk.ModifierType.CONTROL_MASK,
        }
        
        self.assertEqual(expected, parse_keymapping('CONTROL_MASK+KEY_q'))
        
        
    def test_multiple_modifiers(self):
        """
        Test use of several modifiers
        """
        from velouria.config import parse_keymapping
        from gi.repository import Gdk
        
        expected = {
            'key': Gdk.KEY_q,
            'modifiers': Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.META_MASK,
        }
        
        self.assertEqual(expected, parse_keymapping('CONTROL_MASK+META_MASK+KEY_q'))
        
    def test_malformed_input(self):
        """
        Test generally bad input
        """
        from velouria.config import parse_keymapping
        from velouria.exceptions import ConfigKeymappingError
        
        self.assertRaises(ConfigKeymappingError, parse_keymapping, 'CONTROL_MASK META_MASKKEY_q')
        self.assertRaises(ConfigKeymappingError, parse_keymapping, 'dfsadfqefqw3rqwqedasdf')
        
    def test_malformed_key_input(self):
        """
        Test bad key constant input, good mask
        """
        from velouria.config import parse_keymapping
        from velouria.exceptions import ConfigKeymappingError
        
        self.assertRaises(ConfigKeymappingError, parse_keymapping, 'CONTROL_MASK+META_MASKKEY_q')
        
    def test_malformed_mask_input(self):
        """
        Test bad mask input, good key
        """
        from velouria.config import parse_keymapping
        from velouria.exceptions import ConfigKeymappingError
        
        self.assertRaises(ConfigKeymappingError, parse_keymapping, 'CONTROL_MASKXXX+KEY_q')
        
        
class TestParseMulti(TestCase):
    """
    Test the velouria.config.parse_multi function
    """
    
    def test_typical(self):
        """
        Typical successful use
        """
        from velouria.config import parse_multi
        
        expected = ['one', 'two', 'three', 'four', 'five']
        subject = "one \n    two\n\n three\t \n four , five"
        
        self.assertEqual(expected, parse_multi(subject))
        
    def test_oneline(self):
        """
        Only one line provided, comma separated
        """
        from velouria.config import parse_multi
        
        expected = ['one', 'two', 'three', 'four', 'five']
        subject = "one, two,three,four , five"
        
        self.assertEqual(expected, parse_multi(subject))
        
        
    def test_nostrip(self):
        """
        Typical successful use, no stripping
        """
        from velouria.config import parse_multi
        
        expected = ['one ', '    two', ' three\t ', ' four ', ' five']
        subject = "one \n    two\n\n three\t \n four , five"
        
        self.assertEqual(expected, parse_multi(subject, strip=False))
        
        
class TestKeyMappingConfig(TestCase):
    """
    Tests for velouria.config.VelouriaConfigKeyboard
    """
    
    def _defaults(self):
        """
        Helper method to produce the default keymapping for comparison
        """
        from gi.repository import Gdk
        
        defaults = {
            'fullscreen': [
                {
                'key': Gdk.KEY_f,
                'modifiers': Gdk.ModifierType.CONTROL_MASK
                }
            ],
            'pause': [
                {'key': Gdk.KEY_space, 'modifiers': 0},
            ],
            'forward': [
                {'key': Gdk.KEY_Right, 'modifiers': 0},
                {'key': Gdk.KEY_d, 'modifiers': 0},
            ],
            'back': [
                {'key': Gdk.KEY_Left, 'modifiers': 0},
                {'key': Gdk.KEY_a, 'modifiers': 0},
            ],
            'quit': [
                {'key': Gdk.KEY_q, 'modifiers': Gdk.ModifierType.META_MASK},
                {'key': Gdk.KEY_Escape, 'modifiers': 0},
            ],
            'reload': [
                {'key': Gdk.KEY_F5, 'modifiers': 0},
            ],
        }
        
        return defaults
    
    def test_defaults(self):
        """
        Test no config items passed
        """
        from velouria.config import VelouriaConfigKeyboard
        
        keyconfig = VelouriaConfigKeyboard()
        
        expected = self._defaults()
        
        for action in expected.keys():
            self.assertItemsEqual(expected[action], keyconfig[action])
    
    def test_typical(self):
        """
        Test a non-broken, typical setup
        """
        from ConfigParser import ConfigParser
        from velouria.config import VelouriaConfigKeyboard
        from gi.repository import Gdk
        
        config = ConfigParser()
        config.add_section("keyboard")
        config.set("keyboard", "quit", "META_MASK+KEY_q\nKEY_x")
        config.set("keyboard", "fullscreen", "CONTROL_MASK+KEY_r")
        config.set("keyboard", "pause", "")
        
        keyconfig = VelouriaConfigKeyboard(config)
        
        expected = self._defaults()
        
        # override quit and fullscreen actions
        expected['pause'] = None
        expected['quit'] = [
            {'key': Gdk.KEY_x, 'modifiers': 0},
            {'key': Gdk.KEY_q, 'modifiers': Gdk.ModifierType.META_MASK},
        ]
        expected['fullscreen'] = [
            {'key': Gdk.KEY_r, 'modifiers': Gdk.ModifierType.CONTROL_MASK},
        ]
        
        self.assertItemsEqual(expected['quit'], keyconfig.quit)
        self.assertItemsEqual(expected['fullscreen'], keyconfig.fullscreen)
        self.assertIsNone(keyconfig.pause)
        
        
    
