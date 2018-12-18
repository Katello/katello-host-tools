import sys
from os import environ

if sys.version_info[0] == 3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser

def plugin_enabled(filepath, environment_variable, force = False):
    return (force or (config_enabled(filepath) and not environment_disabled(environment_variable))) and not subman_profile_enabled()

def config_enabled(filepath):
    try:
        parser = ConfigParser()
        parser.read(filepath)
        return parser.getint('main', 'enabled') == 1
    except:
        return False

def environment_disabled(variable):
    return variable in environ and environ[variable] != ''

def subman_profile_enabled():
    # subscription-manager versions containing this module
    # provide package-upload and enabled-repos-upload capability
    return 'rhsm.profile.EnabledReposProfile' in sys.modules
