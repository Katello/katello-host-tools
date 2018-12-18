import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from unittest import TestCase

from katello import utils

from mock import patch

ENABLED_CONF = 'test/test_katello/data/plugin_conf/enabled.conf'
DISABLED_CONF = 'test/test_katello/data/plugin_conf/disabled.conf'

class TestPluginEnabled(TestCase):
    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_conf_enabled(self, mock_subman):
        self.assertTrue(utils.plugin_enabled(ENABLED_CONF, 'somevar'))

    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_conf_disabled(self, mock_subman):
        conf = 'test/test_katello/data/plugin_conf/disabled.conf'
        self.assertFalse(utils.plugin_enabled(DISABLED_CONF, 'somevar'))

    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_conf_disabled_force(self, mock_subman):
        self.assertTrue(utils.plugin_enabled(DISABLED_CONF, 'somevar', True))

    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_env_disabled(self, mock_subman):
        os.environ['testa'] = 'true'
        self.assertFalse(utils.plugin_enabled(ENABLED_CONF, 'testa', False))

    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_env_disabled_force(self, mock_subman):
        os.environ['testa'] = 'true'
        self.assertTrue(utils.plugin_enabled(ENABLED_CONF, 'testa', True))

    def test_subman_profile_module_present(self):
        sys.modules["rhsm.profile.EnabledReposProfile"] = True
        self.assertFalse(utils.plugin_enabled(ENABLED_CONF, 'somevar'))

    def test_subman_profile_module_missing(self):
        if "rhsm.profile.EnabledReposProfile" in sys.modules:
            del sys.modules["rhsm.profile.EnabledReposProfile"]

        self.assertTrue(utils.plugin_enabled(ENABLED_CONF, 'somevar'))
