import os
import sys
import unittest2 as unittest
from mock import patch
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))

try:
    from katello import enabled_report
except ImportError:
    print("Yum wasn't present")


class TestEnabledReport(unittest.TestCase):
    @unittest.skipIf('yum' not in sys.modules, "Yum not present")
    def test_root_not_exists(self):
        report = enabled_report.EnabledReport("wrong path")
        self.assertEqual({'enabled_repos': {'repos': []}}, report.content)

    @unittest.skipIf('yum' not in sys.modules, "Yum not present")
    def test_valid(self):
        rh_repo = os.path.join(os.path.dirname(__file__), 'data/repos/redhat.repo')
        report = enabled_report.EnabledReport(rh_repo)
        expected = {'enabled_repos': {'repos': [{'baseurl': ['https://enabled_repo.com'],
                                                 'repositoryid': 'enabled'}]}}

        self.assertEqual(expected, report.content)

    @unittest.skipIf('yum' not in sys.modules, "Yum not present")
    @patch('katello.enabled_report.yum.YumBase.conf')
    def test_var_interpolation_yum(self, yum_base_conf):
        yum_base_conf.yumvar = {'releasever': "6.22", 'basearch': "80286"}
        rh_repo = os.path.join(os.path.dirname(__file__), 'data/repos/redhat.repo.with_vars')
        report = enabled_report.EnabledReport(rh_repo)
        expected = {'enabled_repos': {'repos': [{'baseurl': ['https://enabled_repo.com/6.22/80286'], 'repositoryid': 'enabled_one'}]}}

        self.assertEqual(expected, report.content)
