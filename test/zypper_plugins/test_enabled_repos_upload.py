import os
import sys

from unittest2 import TestCase
import unittest2 as unittest
from mock import Mock, patch

if sys.version_info[0]  == 2:
    from ConfigParser import ConfigParser

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/zypper_plugins'))
    import enabled_repos_upload
except:
  pass

class TestEnabledReposUpload(TestCase):
    def setUp(self):
        self.parser = ConfigParser()
        self.plugin = enabled_repos_upload.EnabledReposUpload()

    @unittest.skipIf('zypp_plugin' not in sys.modules, "zypper not present")
    @patch('enabled_repos_upload.upload_enabled_repos_report')
    def test_plugin_enabled(self, upload_report):
        self.parser.add_section('main')
        self.parser.set('main', 'enabled', 'True')
        self.plugin.PLUGINEND({}, {})

        assert upload_report.called
