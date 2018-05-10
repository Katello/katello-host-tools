import os
import sys
from dnf_support import PluginTestCase, configure_command

import unittest2 as unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/dnf_plugins'))
import package_upload

from mock import Mock, patch


@unittest.skipIf('dnf' not in sys.modules, "DNF not present")
class PackageUploadPluginTest(PluginTestCase):
    def setUp(self):
        super(PackageUploadPluginTest, self).setUp()
        self.plugin = package_upload.PackageUpload(self.base, self.cli)

    @patch('package_upload.PackageUpload.read_config')
    @patch('package_upload.upload_package_profile')
    def test_plugin_enabled(self, upload_profile, read_config):
        self.parser.add_section('main')
        self.parser.set('main', 'enabled', 'True')
        read_config.return_value = self.parser

        self.plugin.transaction()

        assert upload_profile.called

    @patch('package_upload.upload_package_profile')
    def test_plugin_disabled(self, upload_profile):
        self.plugin.transaction()

        assert not upload_profile.called


class PackageUploadCommandTest(unittest.TestCase):
    def setUp(self):
        self.cli = Mock()
        self.command = package_upload.PackageUploadCommand(self.cli)

    @patch('package_upload.upload_package_profile')
    @patch('package_upload.purge_package_cache')
    def test_command_forced(self, remove_cache, upload_profile):
        configure_command(self.command, ['--forceupload'])

        self.command.run()

        assert remove_cache.called
        assert upload_profile.called

    @patch('package_upload.upload_package_profile')
    @patch('package_upload.purge_package_cache')
    def test_command_unforced(self, remove_cache, upload_profile):
        configure_command(self.command, [])

        self.command.run()

        assert not remove_cache.called
        assert upload_profile.called
