import os
import sys

from mock import patch, Mock
import unittest2 as unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/yum-plugins'))
import enabled_repos_upload


FAKE_REPORT = {'foobar': 1}

class TestSendEnabledReport(unittest.TestCase):
    @patch('enabled_repos_upload.EnabledReport')
    @patch('katello.uep.ConsumerIdentity.read')
    @patch('katello.repos.report_enabled_repos')
    @patch('katello.repos.EnabledRepoCache.is_valid')
    @patch('katello.repos.EnabledRepoCache.save')
    def test_send(self, cache_save, cache_valid, fake_report_enabled, fake_read, fake_report):
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

    @patch('enabled_repos_upload.EnabledReport')
    @patch('katello.uep.ConsumerIdentity.read')
    @patch('katello.repos.report_enabled_repos')
    @patch('katello.repos.EnabledRepoCache.is_valid')
    @patch('katello.repos.EnabledRepoCache.save')
    def test_cached(self, cache_save, cache_valid, fake_report_enabled, fake_read, fake_report):
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
