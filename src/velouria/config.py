"""
Velouria: Configuration
=======================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
This module contains classes that parse the velouria.conf file
"""

from gi.repository import Gdk, Gtk
from ConfigParser import ConfigParser, NoSectionError, NoOptionError
from velouria import exceptions, VERSION
import os, sys
import pkg_resources

import logging
from logging.handlers import SysLogHandler, RotatingFileHandler
logger = logging.getLogger("velouria")

log_levels = ('debug', 'info', 'error', 'crit', 'warn')

def common_args(parser):
    """
    Takes a given argparse parser and adds the common config_file,  
    log_level, and log_file options
    """
    paths = config_paths()
    filename = config_file(paths)
    
    parser.add_argument(
        "-c",
        "--config_file",
        metavar="CONFIG_FILE",
        default=filename,
        help="Specify path to a config file. Defaults to %(default)s. \n\n"
    )
    
    parser.add_argument(
        "-v",
        "--log_level",
        choices=('debug', 'info', 'warn', 'error', 'crit'),
        help="Set the log level for output. Defaults to %s" % (VelouriaConfigMain._defaults['log_level'])
    )
    
    parser.add_argument(
        "-l",
        "--log_file",
        help="Set the path of the log file. Three special values are supported: "
             "STDOUT/STDERR - write to standard out or error. SYSLOG - write "
             "to the system log. Defaults to %s" % (VelouriaConfigMain._defaults['log_file'])
    )
    
    parser.epilog = """
       NOTE: Default config file is dynamically divined. Searched: %s
    """ % (", ".join(paths))
    

def setup_logging(log_level, log_file):
    """
    Configure logging - uses some special values for 
    certain situations, like logging to syslog or logging to stdout/stderr
    """
    logger = logging.getLogger('velouria')
    logger.handlers = []
    if log_file == 'SYSLOG':
        # default syslog - assumed /dev/log is a domain socket
        # TODO: use syslog module instead?
        # TODO: is /dev/log ubiquitous? 
        handler = SysLogHandler(address='/dev/log')
        logger.addHandler(handler)
    elif log_file == 'STDERR':
        handler = logging.StreamHandler(sys.stderr)
        logger.addHandler(handler)
    elif log_file == 'STDOUT':
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
    else:
        # assume it's a file
        # add log rotation
        # TODO: make this configurable
        rotator = RotatingFileHandler(log_file, maxBytes=5242880, backupCount=5)
        logger.addHandler(rotator)
        
    set_loglevel(log_level)
    
    return logger

def set_loglevel(level):
    """
    Convert a short name for a log level used in config files, CLI options, 
    to an integer that the logging module can understand, and set the level.
    
    TODO: this could use some refactoring - specifically, enforce D.R.Y.
    TODO: consider merging with setup_logging()
    """
    logger = logging.getLogger('velouria')
    
    if level == 'debug':
        logger.setLevel(logging.DEBUG)
    elif level == 'info':
        logger.setLevel(logging.INFO)
    elif level == 'error':
        logger.setLevel(logging.ERROR)
    elif level == 'crit':
        logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.WARNING)

def coerse_boolean(value):
    """
    Take a text string, trim off leading and trailing whitespace, and return:
    
    True if:
    - value is equal to the word True, On, or Yes (case insensitive)
    - value is a positive number
    - value is equal to the first letter of True/Yes (T/t, Y/y)
    
    False if:
    - value is equal to the word False, Off, or No (case insensitive)
    - value is zero
    - value is equal to the first letter of False/No (F/f, N/n)
    
    None if:
    - the value is an empty string
    
    TODO: handle negative numbers
    """
    orig = value
    value = value.strip()
    value = value.lower()
    
    # short-circuit if the value is empty
    if value == "":
        return None
    
    if value.isdigit():
        value = float(value)
        if value == 0:
            return False
        else:
            return True
    elif value.isalpha():
        if value in ['true', 'yes', 'on', 't', 'y']:
            return True
        elif value in ['false', 'no', 'off', 'n', 'f']:
            return False
        else:
            raise exceptions.ConfigValueError, "%s is not a valid True/False value" % (orig)
    else:
        raise exceptions.ConfigValueError, "%s is not a valid True/False value" % (orig)
            
    
def parse_keymapping(value):
    """
    Given a keymapping string, return a structure with the following format:
    
    {
      modifiers: [modifiers], 
      key: key_constant
    ) 
    
    the modifiers and constants are pulled directly from their sources in the 
    GDK lib.
    
    The keymapping string has the following format:
       SOME_MASK+SOME_OTHER_MASK+KEY_CONSTANT
    
    NOTE: any constant can be used for the 'key', including mouse clicks. Untested.
    
    TODO: handle multiple keys (multiple modifiers are implemented with one key)
    """
    output = {
        'modifiers': 0,
        'key': None
    }
    
    parts = value.split("+")
    if len(parts) > 1:
        modifiers = parts[:-1]
        key = parts[-1:][0].strip()
    else:
        modifiers = []
        key = parts[0].strip()
    
    for modifier in modifiers:
        modifier = modifier.strip()
        got = getattr(Gdk.ModifierType, modifier, None)
        
        if got:
            if not output['modifiers']:
                output['modifiers'] = got
            else:
                output['modifiers'] = output['modifiers'] | got
        else:
            raise exceptions.ConfigKeymappingError, "Modifier %s could not be found in Gdk.ModifierType." % (modifier)
            
            
    got_key = getattr(Gdk, key, None)
    
    if got_key:
        output['key'] = got_key
    else:
        raise exceptions.ConfigKeymappingError, "Key constant %s could not be found in Gdk." % (key)
        
    return output

def parse_multi(content, strip=True, always_list=True):
    """
    Config options that take multiple values support the following formatitng 
    options:
    
    - commas
    - newlines
    
    Example:
    
    [test]
    option = first value
             second value, third value
             fourth value
             
    Will return ['first value', 'second value', 'third value', 'fourth value']
    
    TODO: handle values that need to contain newlines or commas
    TODO: return None if there are no members?
    TODO: return a single value if there is only one member?
    """
    content = content.replace(",", "\n")
    parts = content.splitlines()
    
    if strip:
        output = [x.strip() for x in parts]
    else:
        output = parts
        
    # remove any empty entries
    output = [x for x in output if x != '']
    
    if always_list:
        return output
    
    if len(output) == 1:
        return output[0]
    elif len(output) == 0:
        return None
    else:
        return output
    

class VelouriaConfigSection(object):
    """
    Base class for data structures that represent one section of
    velouria.conf.
    
    Provides a mechanism for setting defaults, post-processing of
    info.
    
    Creates a obj.option-style interface.
    
    TODO: devise a way to also pull config overrides from the command line
    """
    # the name of the section to look for
    _name = None
    
    # dictionary of default values (also defines possible values)
    _defaults = None
    
    # raw section data
    _section = None
    
    # parsed data
    _data = None
    
    # reference back to the parent ConfigParser object
    _config = None
    
    # always return a list when parsing multi-line objects
    _always_list = True
    
    def __init__(self, config=None, name=None):
        if name:
            self._name = name
            
        self._config = config
        
        self.load_defaults()
        self.load_section(config)
        self.load()
    
    def load_section(self, config):
        """
        Grab the section for this config object, setting a default value
        if it doesn't exist
        """
        try:
            self._section = config.items(self._name)
        except (NoSectionError, AttributeError):
            # raises NoSectionError if the section is missing, AttributeError
            # if config is None or doesn't have an items() method.
            logging.warn("No section found for %s", self._name)
            self._section = [x for x in self._defaults.iteritems()]
    
    def load_defaults(self):
        """
        Pre-populate the _data dictionary with the default values
        """
        self._data = {}
        for key, val in self._defaults.iteritems():
            self._data[key] = self.process_option(key, val)
        
    
    def process_option(self, name, value):
        """
        Hook for doing your own thing with processing specific 
        values
        """
        return parse_multi(value, always_list=self._always_list)
    
    def load(self):
        """
        Parse the ConfigParser data and set up internal structures as needed
        """
        
        for key, val in self._section:
            self._data[key] = self.process_option(key, val)
        
    
    def __getattr__(self, key):
        if key in self._defaults.keys():
            return self._data[key]
        else:
            raise AttributeError, "'%s' object has no attribute '%s'" % (self.__class__.__name__, key)
    
    def __getitem__(self, key):
        if key in self._defaults.keys():
            return self._data[key]
        else:
            raise KeyError, key
            
    def __iter__(self):
        return self._data.iteritems()

class VelouriaConfigMain(VelouriaConfigSection):
    """
    Data structure used to set defaults for, and hold values of,
    the [main] section in velouria.conf
    """
    _always_list = False
    
    _defaults = {
        'keyboard_control':'off',
        'slides':'',
        'width': '400',
        'height': '400',
        'title': "Velouria v. %s" % VERSION,
        'paused_on_start': 'off',
        'fullscreen_on_start': 'on',
        'socket_file': '/tmp/velouria.sock',
        'log_level': 'info',
        'log_file': 'velouria.log',
    }
    
    _name="main"
    
    def process_option(self, name, value):
        if name in ('keyboard_control', 'paused_on_start', 'fullscreen_on_start'):
            return coerse_boolean(value)
        elif name == 'slides':
            return parse_multi(value, always_list=True)
        elif name in ('width', 'height'):
            try:
                val =  int(value)
                if val < 0:
                    raise ValueError
                return val
            except ValueError:
                raise exceptions.ConfigValueError, "'%s' is not a valid pixel %s" % (value, name)
        elif name == 'log_level':
            if not value in log_levels:
                raise exceptions.ConfigValueError, "'%s' is not a valid logging level" % (value)
            else:
                return value
        elif name == 'log_file':
            if not value in ('SYSLOG', 'STDOUT', 'STDERR'):
                return os.path.abspath(value)
            else:
                return value
        else:
            return super(VelouriaConfigMain, self).process_option(name, value)
    
    
class VelouriaConfigSlideDeck(object):
    """
    Wrapper object around a series of VelouriaConfigSlide objects
    """
    slides = None
    
    main = None
    
    def __init__(self, main):
        """
        Given an initialized VelouriaConfigMain object, present a data
        structure that allows easy access to individual slide config info
        
        Given a config file like this:
        
        [main]
        keyboard_control = off
        slides = 
            slide1
            slide3
            slideawesome
        
        [slideawesome]
        type = slide-entry-point
        uri = blah
        
        Creates a data structure like this:
        
        obj = VelouriaConfigSlideDeck(main)
        obj[slide1] = ('slide-entry-point', BrowserSlideClass)
        """
        
        self.slides = None
        self.main = main
        
        self.classes = {}
        
        for ep in pkg_resources.iter_entry_points('velouria.slide'):
            self.classes[ep.name] = ep.load()
        
        self.slides = []
        
        for slide in main.slides:
            try:
                type_ = main._config.get(slide, 'type')
                class_ = self.classes[type_]
            except NoOptionError:
                # default slide type: web browser
                type_ = 'browser'
                class_ = self.classes[type_]
            except NoSectionError:
                raise exceptions.ConfigValueError, "There is no '%s' section" % (slide)
            except KeyError:
                raise exceptions.ConfigValueError, "Could not find class for specified type '%s'" % (type_)
                
            if class_ == None:
                raise exceptions.ConfigValueError, "Could not find class for specified type '%s'" % (type_)
                
            self.slides.append((slide, type_, class_))
        
    def __iter__(self):
        return iter(self.slides)
    
class VelouriaConfigKeyboard(VelouriaConfigSection):
    """
    Data structure used to set defaults for, and hold values of,
    the [keyboard] section in velouria.conf
    
    Handles interpretation of key mappings for various actions.
    """
    _name = "keyboard"
    
    _defaults = {
        'fullscreen': 'CONTROL_MASK+KEY_f',
        'pause': 'KEY_space',
        'forward': 'KEY_Right, KEY_d',
        'back': 'KEY_Left, KEY_a',
        'quit': 'KEY_Escape, META_MASK+KEY_q',
        'reload': 'KEY_F5',
    }
    
    def process_option(self, name, value):
        params = parse_multi(value, always_list=True)
        if params:
            return [parse_keymapping(x) for x in params]
        else:
            return None

def config_paths(paths=None, filename="velouria.conf"):
    """
    used to query what the default paths are for the 
    config file. 
    
    Looks in the following directories (in that order), using the first
    file it finds, if paths is not provided:
    
        - the current working directory
        - $HOME/
        - /usr/local
        - /etc
    """
    output = []
    
    if not paths:
        paths = [
            os.getcwd(),
            os.path.expanduser("~"),
            '/usr/local',
            '/etc'
        ]
    
    for prefix in paths:
        path = os.path.join(prefix, filename)
        output.append(os.path.abspath(os.path.expanduser(path)))
        
    return output
    
def config_file(paths):
    """
    Loops through a list of paths, and returns the first file it finds,
    or None if it can't find any
    
    TODO: raise an error here if the files cannot be found?
    """
    for path in paths:
        if os.path.exists(path):
            return path

class VelouriaConfig(object):
    """
    Reads the velouria.conf file, sets defaults, and provides 
    helper methods for constructing dynamic widgets based on
    the config file
    """
    # internal configparser object
    config = None
    
    # keyboard info
    keyboard = None
    
    # main info
    main = None
    
    # slide info
    slides = None
    
    # global style sheet
    style = None
    
    # config file path
    config_file_path = None
    
    def set_style(self):
        data =  "* {\n" \
                "-GtkButton-default-border : 0px;\n" \
                "-GtkButton-default-outside-border : 0px;\n" \
                "-GtkButton-inner-border: 0px;\n" \
                "-GtkWidget-focus-line-width : 0px;\n" \
                "-GtkWidget-focus-padding : 0px;\n" \
                "padding: 0px;\n" \
                "}"
        provider = Gtk.CssProvider()
        provider.load_from_data(data)
        self.style = provider
    
    def load(self, config_file_path=None):
        
        if not config_file_path:
            paths = config_paths()
            config_file_path = config_file(paths)
        
        logger.info("Loading config file %s", config_file_path)
        
        self.config = ConfigParser()
        
        parsed = self.config.read([config_file_path,])
        
        if not parsed:
            raise exceptions.ConfigError, "No config file file could be found"
        
        self.keyboard = VelouriaConfigKeyboard(self.config)
        
        self.main = VelouriaConfigMain(self.config)
        
        self.slides = VelouriaConfigSlideDeck(self.main)
        
        self.config_file_path = config_file_path
    
    def __init__(self, config_file_path=None):
        """
        Parse a velouria.conf file.
        """
        self.load(config_file_path)
        
        self.set_style()
