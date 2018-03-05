import errno
import os
import sys

from katello.constants import PACKAGE_CACHE_FILE
from katello.uep import get_manager


def upload_package_profile():
    get_manager().profilelib._do_update()


def purge_package_cache():
    try:
        os.remove(PACKAGE_CACHE_FILE)
    except OSError:
        error = sys.exc_info()[1]  # backward and forward compatible way to get the exception
        if error.errno is not errno.ENOENT:
            sys.stderr.write("Unable to clear the package cache")
