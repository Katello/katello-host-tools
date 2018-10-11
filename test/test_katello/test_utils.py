import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from unittest import TestCase

from katello import utils

from mock import patch

class TestUtils(TestCase):
    def test_plugin_enabled(self):
        conf = 'test/test_katello/data/plugin_conf/enabled.conf'
        self.assertTrue(utils.plugin_enabled(conf))

    def test_plugin_enabled_disabled(self):
        conf = 'test/test_katello/data/plugin_conf/disabled.conf'
        self.assertFalse(utils.plugin_enabled(conf))

