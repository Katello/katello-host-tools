import sys
import os
from os import environ

if sys.version_info[0] == 3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser


def plugin_enabled(filepath, environment_variable=None, force=False):
    return force or (config_enabled(filepath) and not environment_disabled(environment_variable))


def config_enabled(filepath):
    try:
        parser = ConfigParser()
        parser.read(filepath)
        return parser.getint('main', 'enabled') == 1
    except:
        return False


def environment_disabled(variable):
    return variable is not None and variable in environ and environ[variable] != ''


def combined_profiles_enabled():
    try:
        from rhsm.profile import EnabledRepos
        # flake8: noqa
        return True
    except ImportError:
        return False


def is_root_user():
    return os.getuid() == 0
