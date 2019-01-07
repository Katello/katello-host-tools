import os
import sys
from unittest import TestCase

from mock import Mock, patch
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))

from katello import utils


if sys.version_info[0] == 3:
    from configparser import NoOptionError
else:
    from ConfigParser import NoOptionError

ENABLED_CONF = 'test/test_katello/data/plugin_conf/enabled.conf'
DISABLED_CONF = 'test/test_katello/data/plugin_conf/disabled.conf'


class TestPluginEnabled(TestCase):
    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_conf_enabled(self, mock_subman):
        self.assertTrue(utils.plugin_enabled(ENABLED_CONF))

    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_conf_disabled(self, mock_subman):
        self.assertFalse(utils.plugin_enabled(DISABLED_CONF))

    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_conf_disabled_force(self, mock_subman):
        self.assertTrue(utils.plugin_enabled(DISABLED_CONF, None, True))

    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_env_disabled(self, mock_subman):
        os.environ['testa'] = 'true'
        self.assertFalse(utils.plugin_enabled(ENABLED_CONF, 'testa'))

    @patch('katello.utils.subman_profile_enabled', return_value=False)
    def test_env_disabled_force(self, mock_subman):
        os.environ['testa'] = 'true'
        self.assertTrue(utils.plugin_enabled(ENABLED_CONF, 'testa', True))

    @patch('katello.utils.rhsmConfig.initConfig')
    def test_subman_profile_enabled(self, mock_init):
        mock_config = Mock()
        mock_init.return_value = mock_config
        mock_config.get.return_value = '1'

        self.assertFalse(utils.plugin_enabled(ENABLED_CONF))
        mock_config.get.assert_called_with('rhsm', 'package_profile_on_trans')

    @patch('katello.utils.rhsmConfig.initConfig')
    def test_subman_profile_enabled_disabled(self, mock_init):
        mock_config = Mock()
        mock_init.return_value = mock_config
        mock_config.get.return_value = '0'

        self.assertTrue(utils.plugin_enabled(ENABLED_CONF))
        mock_config.get.assert_called_with('rhsm', 'package_profile_on_trans')

    @patch('katello.utils.rhsmConfig.initConfig')
    def test_subman_profile_enabled_missing_config_key(self, mock_init):
        mock_config = Mock()
        mock_init.return_value = mock_config
        mock_config.get.side_effect = NoOptionError('rhsm', 'package_profile_on_trans')

        self.assertTrue(utils.plugin_enabled(ENABLED_CONF))
        mock_config.get.assert_called_with('rhsm', 'package_profile_on_trans')
