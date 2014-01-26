"""
Velouria: Exceptions
====================
Velouria: a plugable, configurable, resource-conservative information
          kiosk application
          
Exceptions raised by the application are collected here.
"""

class ConfigError(Exception):
    """
    Raised when there is a problem processing the configuration file
    """
    
class ConfigValueError(ConfigError):
    """
    Raised when a value from the config file cannot be parsed
    """
    
class ConfigKeymappingError(ConfigError):
    """
    Raised when a key mapping cannot be parsed.
    """
