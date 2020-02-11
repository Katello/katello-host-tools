import errno
import os
import sys

from katello.constants import DISABLE_PACKAGE_PROFILE_VAR, PACKAGE_CACHE_FILE, PACKAGE_PROFILE_PLUGIN_CONF, PROFILE_CACHE_FILE
from katello.uep import get_manager, lookup_consumer_id
from katello.utils import combined_profiles_enabled, plugin_enabled


def upload_package_profile(force=False):
    if not plugin_enabled(PACKAGE_PROFILE_PLUGIN_CONF, DISABLE_PACKAGE_PROFILE_VAR, force):
        return

    consumer_id = lookup_consumer_id()
    if consumer_id is None:
        sys.stderr.write("Cannot upload package profile. Is this client registered?\n")
    else:
        get_manager().profilelib._do_update()


def purge_package_cache():
    file_to_remove = PACKAGE_CACHE_FILE
    if combined_profiles_enabled():
        file_to_remove = PROFILE_CACHE_FILE
    try:
        os.remove(file_to_remove)
    except OSError:
        error = sys.exc_info()[1]  # backward and forward compatible way to get the exception
        if error.errno is not errno.ENOENT:
            sys.stderr.write("Unable to clear the package cache")
