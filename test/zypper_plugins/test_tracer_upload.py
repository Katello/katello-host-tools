import os
import sys

import unittest
from mock import Mock, patch

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/zypper_plugins'))
    import tracer_upload
except:
    pass

class TestTracerUpload(unittest.TestCase):
    def setUp(self):
        self.plugin = tracer_upload.TracerUploadPlugin()

    @unittest.skipIf('zypp_plugin' not in sys.modules, "zypper not present")
    @patch('tracer_upload.upload_tracer_profile')
    def test_plugin_enabled(self, upload_tracer):
        self.plugin.PLUGINEND({}, {})
        assert upload_tracer.called
