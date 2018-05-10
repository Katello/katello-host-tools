try:
    import json
except ImportError:
    import simplejson as json
import os
import sys

from unittest2 import TestCase

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from katello import repos

from mock import patch


class TestEnabledRepoCache(TestCase):
    CACHE_FILE = '/tmp/repo_cache.json'  #Override default cache due to /var/cache perms

    @patch('katello.repos.ENABLED_REPOS_CACHE_FILE', CACHE_FILE)
    def test_invalid_no_cache(self):
        try:
            os.remove(self.CACHE_FILE)
        except OSError:
            pass

        cache = repos.EnabledRepoCache(None, {})

        assert not cache.is_valid()

    @patch('katello.repos.ENABLED_REPOS_CACHE_FILE', CACHE_FILE)
    def test_invalid_with_malformed_cache(self):
        self.write_cache('')

        cache = repos.EnabledRepoCache(None, None)

        # raise ValueError
        assert not cache.is_valid()

    @patch('katello.repos.ENABLED_REPOS_CACHE_FILE', CACHE_FILE)
    def test_valid(self):
        data = json.dumps({'foo': {}})
        self.write_cache(data)

        cache = repos.EnabledRepoCache('foo', {})

        assert cache.is_valid()

    def write_cache(self, data):
        cache_file = open(self.CACHE_FILE, 'w')
        cache_file.write(data)
        cache_file.close()
