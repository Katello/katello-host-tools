import os
import sys

from rhsm.connection import RemoteServerException

from mock import patch, Mock
import unittest2 as unittest

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/yum-plugins'))
    import enabled_repos_upload
except ImportError:
    print("Yum wasn't present")


FAKE_REPORT = {'foobar': 1}

class TestSendEnabledReport(unittest.TestCase):
    @patch('katello.repos.plugin_enabled', return_value=True)
    @patch('enabled_repos_upload.EnabledReport')
    @patch('katello.uep.ConsumerIdentity.read')
    @patch('katello.repos.report_enabled_repos')
    @patch('katello.repos.EnabledRepoCache.is_valid')
    @patch('katello.repos.EnabledRepoCache.save')
    @unittest.skipIf(sys.version_info[0] > 2, "yum tests for PY2 only")
    def test_send(self, cache_save, cache_valid, fake_report_enabled, fake_read, fake_report, plugin_enabled):
        consumer_id = '1234'
        fake_certificate = Mock()
        fake_certificate.getConsumerId.return_value = consumer_id
        fake_read.return_value = fake_certificate
        cache_valid.return_value = False

        report = Mock()
        fake_report.return_value = report
        report.content = FAKE_REPORT

        enabled_repos_upload.upload_enabled_repos_report(report)

        # validation
        fake_certificate.getConsumerId.assert_called_with()
        fake_report_enabled.assert_called_with(consumer_id, FAKE_REPORT)

    @patch('katello.repos.plugin_enabled', return_value=True)
    @patch('enabled_repos_upload.EnabledReport')
    @patch('katello.uep.ConsumerIdentity.read')
    @patch('katello.repos.report_enabled_repos')
    @patch('katello.repos.EnabledRepoCache.is_valid')
    @patch('katello.repos.EnabledRepoCache.save')
    @unittest.skipIf(sys.version_info[0] > 2, "yum tests for PY2 only")
    def test_cached(self, cache_save, cache_valid, fake_report_enabled, fake_read, fake_report, plugin_enabled):
        consumer_id = '1234'
        fake_certificate = Mock()
        fake_certificate.getConsumerId.return_value = consumer_id
        fake_read.return_value = fake_certificate
        cache_valid.return_value = True

        report = Mock()
        fake_report.return_value = report
        report.content = FAKE_REPORT

        enabled_repos_upload.upload_enabled_repos_report(report)

        # validation
        fake_certificate.getConsumerId.assert_called_with()
        fake_report_enabled.assert_not_called()

    @patch('katello.repos.get_uep')
    @patch('katello.repos.lookup_consumer_id')
    @patch('katello.repos.EnabledRepoCache.is_valid')
    @patch('katello.repos.EnabledRepoCache.save')
    @unittest.skipIf(sys.version_info[0] > 2, "yum tests for PY2 only")
    def test_http_fail(self, cache_save, cache_valid, fake_consumer_id, fake_uep):
        fake_uep().conn.request_put.side_effect = RemoteServerException(500)
        cache_valid.return_value = False

        enabled_repos_upload.upload_enabled_repos_report(Mock())

        # validation
        cache_save.assert_not_called()
