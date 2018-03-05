import os
import sys
from test.dnf_support import PluginTestCase, configure_command
from unittest import TestCase

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from dnf_plugins import enabled_repos_upload

from mock import Mock, patch


class TestEnabledReposUploadPlugin(PluginTestCase):
    def setUp(self):
        super(TestEnabledReposUploadPlugin, self).setUp()
        self.plugin = enabled_repos_upload.EnabledReposUpload(self.base, self.cli)

    @patch('dnf_plugins.enabled_repos_upload.EnabledReposUpload.read_config')
    @patch('dnf_plugins.enabled_repos_upload.upload_enabled_repos_report')
    def test_plugin_enabled(self, upload_report, read_config):
        self.parser.add_section('main')
        self.parser.set('main', 'enabled', 'True')
        read_config.return_value = self.parser

        self.plugin.transaction()

        assert upload_report.called

    @patch('dnf_plugins.enabled_repos_upload.upload_enabled_repos_report')
    def test_plugin_disabled(self, upload_report):
        self.plugin.transaction()

        assert not upload_report.called


class TestUploadCommand(TestCase):
    def setUp(self):
        self.cli = Mock()
        self.command = enabled_repos_upload.UploadReposCommand(self.cli)

    @patch('dnf_plugins.enabled_repos_upload.upload_enabled_repos_report')
    @patch('dnf_plugins.enabled_repos_upload.EnabledRepoCache.remove_cache')
    def test_command_unforced(self, remove_cache, upload_report):
        configure_command(self.command, [])

        self.command.run()

        assert not remove_cache.called
        assert upload_report.called

    @patch('dnf_plugins.enabled_repos_upload.upload_enabled_repos_report')
    @patch('dnf_plugins.enabled_repos_upload.EnabledRepoCache.remove_cache')
    def test_command_forced(self, remove_cache, upload_report):
        configure_command(self.command, ['--forceupload'])

        self.command.run()

        assert remove_cache.called
        assert upload_report.called
