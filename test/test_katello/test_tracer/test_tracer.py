import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from katello.tracer import upload_tracer_profile, query_affected_apps
from katello.constants import YUM, ZYPPER

from mock import patch

class TestUploadTracerProfile(unittest.TestCase):
    def _query_affected_apps(self, plugin=None):
        return []

    @patch('katello.tracer.get_uep')
    @patch('katello.tracer.lookup_consumer_id')
    def test_tracer_upload_registered(self, mock_lookup, mock_uep):
        mock_lookup.return_value = True

        upload_tracer_profile(self._query_affected_apps)

        mock_uep().conn.request_put.assert_called()

    @patch('katello.tracer.get_uep')
    @patch('katello.tracer.lookup_consumer_id')
    def test_tracer_upload_unregistered(self, mock_lookup, mock_uep):
        mock_lookup.return_value = None

        upload_tracer_profile(self._query_affected_apps)

        mock_uep().conn.request_put.assert_not_called()

class TestQueryAffectedApps(unittest.TestCase):
    @unittest.skipIf(YUM == False, "Yum not present")
    def test_el_os(self):
        self.assertEqual(query_affected_apps(), [])

    @unittest.skipIf(ZYPPER == False, "ZYPPER not present")
    def test_zypper_os(self):
        self.assertEqual(query_affected_apps(), [])
