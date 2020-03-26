import errno
import os
import os.path
import sys

from katello.constants import DISABLE_ENABLE_REPOS_VAR, ENABLED_REPOS_CACHE_FILE, ENABLED_REPOS_PLUGIN_CONF, PROFILE_CACHE_FILE
from katello.uep import get_manager, get_uep, lookup_consumer_id
from katello.utils import combined_profiles_enabled, plugin_enabled

from rhsm.connection import GoneException, RemoteServerException

try:
    import json
except ImportError:
    import simplejson as json


def error_message(msg):
    sys.stderr.write(msg + "\n")


def report_enabled_repos(consumer_id, report):
    """
    Report enabled repositories to the UEP.
    :param consumer_id: The consumer ID.
    :type consumer_id: str
    :param report: The report to send.
    :type report: dict
    """
    uep = get_uep()
    method = '/systems/%s/enabled_repos' % uep.sanitize(consumer_id)
    try:
        uep.conn.request_put(method, report)
        return True
    except (RemoteServerException, GoneException):
        error = sys.exc_info()[1]  # backward and forward compatible way to get the exception
        error_message(str(error))


def upload_enabled_repos_report(report, force=False):
    if not plugin_enabled(ENABLED_REPOS_PLUGIN_CONF, DISABLE_ENABLE_REPOS_VAR, force):
        return
    consumer_id = lookup_consumer_id()
    if consumer_id is None:
        error_message('Cannot upload enabled repos report, is this client registered?')
    elif report is None:
        get_manager().profilelib._do_update()
    else:
        content = report.content
        cache = EnabledRepoCache(consumer_id, content)
        if not cache.is_valid() and report_enabled_repos(consumer_id, content):
            cache.save()


class EnabledRepoCache:
    def __init__(self, consumer_id, content):
        self.consumer_id = consumer_id
        self.content = content

    @staticmethod
    def remove_cache():
        file_to_remove = ENABLED_REPOS_CACHE_FILE
        if combined_profiles_enabled():
            file_to_remove = PROFILE_CACHE_FILE
        try:
            os.remove(file_to_remove)
        except OSError:
            pass

    def is_valid(self):
        cache_file = None
        # wrapper try block w/ finally needed for python 2.4
        try:
            try:
                cache_file = open(ENABLED_REPOS_CACHE_FILE, 'r')
                try:
                    return self.data() == json.loads(cache_file.read())
                except ValueError:
                    return False
            except IOError:
                error = sys.exc_info()[1]  # backward and forward compatible way to get the exception
                if error.errno == errno.ENOENT:
                    return False
        finally:
            if cache_file is not None:
                cache_file.close()

    def data(self):
        return {self.consumer_id: self.content}

    def save(self):
        cache_dir = os.path.dirname(ENABLED_REPOS_CACHE_FILE)
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)

        cache_file = None
        try:
            cache_file = open(ENABLED_REPOS_CACHE_FILE, 'w')
            cache_file.write(json.dumps(self.data()))
        finally:
            if cache_file is not None:
                cache_file.close()
