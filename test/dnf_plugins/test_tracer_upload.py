import os
import sys
from test.dnf_support import PluginTestCase, configure_command
import unittest2 as unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/dnf_plugins'))
import tracer_upload

from mock import Mock, patch


@unittest.skipIf(sys.version_info[0] < 3, "dnf plugins should use PY3")
class TestTracerPlugin(PluginTestCase):
    def setUp(self):
        super(TestTracerPlugin, self).setUp()
        self.plugin = tracer_upload.TracerUpload(self.base, self.cli)

    @patch('tracer_upload.TracerUpload.read_config')
    @patch('tracer_upload.upload_tracer_profile')
    def test_plugin_enabled(self, upload_tracer, read_config):
        self.parser.add_section('main')
        self.parser.set('main', 'enabled', 'True')
        read_config.return_value = self.parser
        self.plugin.transaction()

        assert upload_tracer.called

    @patch('tracer_upload.upload_tracer_profile')
    def test_plugin_disabled(self, upload_tracer):
        self.plugin.transaction()

        assert not upload_tracer.called


class TestTracerUploadCommand(unittest.TestCase):
    def setUp(self):
        self.cli = Mock()
        self.command = tracer_upload.TracerUploadCommand(self.cli)

    @patch('tracer_upload.upload_tracer_profile')
    def test_command(self, upload_profile):
        configure_command(self.command, [])

        self.command.run()

        assert upload_profile.called
