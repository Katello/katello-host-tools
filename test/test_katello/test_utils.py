import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from unittest import TestCase

from katello import utils

from mock import patch

ENABLED_CONF = 'test/test_katello/data/plugin_conf/enabled.conf'
DISABLED_CONF = 'test/test_katello/data/plugin_conf/disabled.conf'

class TestUtils(TestCase):
    def test_plugin_enabled(self):
        self.assertTrue(utils.plugin_enabled(ENABLED_CONF, 'somevar'))

    def test_plugin_enabled_disabled(self):
        conf = 'test/test_katello/data/plugin_conf/disabled.conf'
        self.assertFalse(utils.plugin_enabled(DISABLED_CONF, 'somevar'))

    def test_plugin_enabled_disabled_force(self):
        self.assertTrue(utils.plugin_enabled(DISABLED_CONF, 'somevar', True))

    def test_plugin_enabled_disabled_var(self):
        os.environ['testa'] = 'true'
        self.assertFalse(utils.plugin_enabled(ENABLED_CONF, 'testa', False))

    def test_plugin_enabled_disabled_var_force(self):
        os.environ['testa'] = 'true'
        self.assertTrue(utils.plugin_enabled(ENABLED_CONF, 'testa', True))