import os
import sys

import unittest
from mock import Mock, patch

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/zypper_plugins'))
    import enabled_repos_upload
except:
  pass

class TestEnabledReposUpload(unittest.TestCase):
    def setUp(self):
        self.plugin = enabled_repos_upload.EnabledReposUpload()

    @unittest.skipIf('zypp_plugin' not in sys.modules, "zypper not present")
    @patch('enabled_repos_upload.upload_enabled_repos_report')
    def test_plugin_enabled(self, upload_report):
        self.plugin.PLUGINEND({}, {})

        assert upload_report.called
