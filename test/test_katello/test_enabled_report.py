import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from unittest import TestCase

from katello import enabled_report

from mock import patch

class TestEnabledReport(TestCase):
    def test_root_not_exists(self):
        report = enabled_report.EnabledReport("wrong path")
        self.assertEqual({'enabled_repos': {'repos': []}}, report.content)

    def test_valid(self):
        rh_repo = os.path.join(os.path.dirname(__file__), 'data/repos/redhat.repo')
        report = enabled_report.EnabledReport(rh_repo)
        expected = {'enabled_repos': {'repos': [{'baseurl': ['https://enabled_repo.com'],
                               'repositoryid': 'enabled'}]}}

        self.assertEqual(expected, report.content)

    @patch('katello.enabled_report.EnabledReport._obtain_mappings_dnf')
    def test_var_interpolation_dnf(self, mock_obtain_mappings_dnf):
        mock_obtain_mappings_dnf.return_value = {'releasever': "6.22", 'basearch': "80286"}
        rh_repo = os.path.join(os.path.dirname(__file__), 'data/repos/redhat.repo.with_vars')
        report = enabled_report.EnabledReport(rh_repo)
        expected = {'enabled_repos': {'repos': [{'baseurl': ['https://enabled_repo.com/6.22/80286'], 'repositoryid': 'enabled_one'}]}}

        self.assertEqual(expected, report.content)

    @patch('katello.enabled_report.EnabledReport._obtain_mappings_yum')
    @patch('katello.enabled_report.EnabledReport._obtain_mappings_dnf')
    def test_var_interpolation_yum(self, mock_obtain_mappings_dnf, mock_obtain_mappings_yum):
        mock_obtain_mappings_dnf.side_effect = ImportError("dnf not available on 80286")
        mock_obtain_mappings_yum.return_value = {'releasever': "6.22", 'basearch': "80286"}
        rh_repo = os.path.join(os.path.dirname(__file__), 'data/repos/redhat.repo.with_vars')
        report = enabled_report.EnabledReport(rh_repo)
        expected = {'enabled_repos': {'repos': [{'baseurl': ['https://enabled_repo.com/6.22/80286'], 'repositoryid': 'enabled_one'}]}}

        self.assertEqual(expected, report.content)
