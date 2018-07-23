import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from unittest import TestCase

from katello.agent.pulp import handler
try:
    from katello.agent.pulp import libdnf as system_lib
except ImportError:
    from katello.agent.pulp import libyum as system_lib

from mock import patch

class PackageHandler(TestCase):
    @patch(system_lib.__name__ + '.Package.update')
    def test_update(self, mock_update):
        pkg_handler = handler.PackageHandler()
        mock_update.return_value = {'failed': False, 'resolved': [], 'deps': []}

        report = pkg_handler.update([{'name': 'foo'}], {})

        assert report.succeeded
        mock_update.assert_called_with([system_lib.Pattern('foo')])

    @patch(system_lib.__name__ + '.Package.update')
    def test_update_all(self, mock_update):
        pkg_handler = handler.PackageHandler()
        mock_update.return_value = {'failed': False, 'resolved': [], 'deps': []}

        report = pkg_handler.update([{}], {'all': True})
 
        assert report.succeeded
        mock_update.assert_called_with([])

        
