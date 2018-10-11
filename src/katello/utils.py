import sys

if sys.version_info[0] == 3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser

def plugin_enabled(filepath):
    parser = ConfigParser()
    parser.read(filepath)
    return parser.getint('main', 'enabled') == 1

