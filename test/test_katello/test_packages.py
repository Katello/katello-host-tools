import os
import sys
from unittest import TestCase

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from katello.packages import purge_package_cache, upload_package_profile

from mock import patch


class TestUploadPackageProfile(TestCase):
    @patch('katello.packages.plugin_enabled', return_value=True)
    @patch('katello.packages.get_manager')
    @patch('katello.packages.lookup_consumer_id')
    def test_upload_registered(self, mock_lookup, mock_manager, plugin_enabled):
        mock_lookup.return_value = True

        upload_package_profile()

        mock_manager.return_value.profilelib._do_update.assert_called()

    @patch('katello.packages.get_manager')
    @patch('katello.packages.lookup_consumer_id')
    def test_upload_unregistered(self, mock_lookup, mock_manager):
        mock_lookup.return_value = None

        upload_package_profile()

        mock_manager.assert_not_called()


class TestPurgePackageCache(TestCase):

    @patch('katello.packages.os')
    def test_purge(self, mock_os):
        purge_package_cache()

        mock_os.remove.assert_called_with('/var/lib/rhsm/cache/profile.json')
