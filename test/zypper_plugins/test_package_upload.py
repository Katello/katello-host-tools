import os
import sys

from unittest2 import TestCase
import unittest2 as unittest
from mock import Mock, patch

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/zypper_plugins'))
    import package_upload
except:
  pass

class TestPackageUpload(TestCase):
    def setUp(self):
        self.plugin = package_upload.KatelloZyppPlugin()

    @unittest.skipIf('zypp_plugin' not in sys.modules, "zypper not present")
    @patch('package_upload.upload_package_profile')
    def test_plugin_enabled(self, upload_package_profile):
        self.plugin.PLUGINEND({}, {})

        assert upload_package_profile.called
