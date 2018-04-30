import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from unittest2 import TestCase

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
