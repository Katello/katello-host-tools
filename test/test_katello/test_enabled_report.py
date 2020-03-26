import os
import sys
import unittest2 as unittest
from mock import patch
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))
from katello import enabled_report
from katello.constants import YUM, ZYPPER

class TestEnabledReport(unittest.TestCase):
    @unittest.skipIf(YUM == False, "Yum not present")
    def test_root_not_exists(self):
        report = enabled_report.EnabledReport("wrong path")
        self.assertEqual({'enabled_repos': {'repos': []}}, report.content)

    @unittest.skipIf(YUM == False, "Yum not present")
    def test_yum_valid(self):
        rh_repo = os.path.join(os.path.dirname(__file__), 'data/repos/redhat.repo')
        report = enabled_report.EnabledReport(rh_repo)
        expected = {'enabled_repos': {'repos': [{'baseurl': ['https://enabled_repo.com'],
                                                 'repositoryid': 'enabled'}]}}

        self.assertEqual(expected, report.content)

    @unittest.skipIf(ZYPPER == False, "Zypper not present")
    @patch('katello.enabled_report.YUM', False)
    def test_zypper_valid(self):
        rh_repo = os.path.join(os.path.dirname(__file__), 'data/repos/redhat.repo.suse')
        report = enabled_report.EnabledReport(rh_repo)
        expected = {'enabled_repos': {'repos': [{'baseurl': ['https://katello.example.com/pulp/repos/Dev/Library/Suse_15_SP1_v2/custom/Python_2_Module_15_SP1_x86_64/Python_2_Module_15_SP1_x86_64_SLE-Module-Python2-15-SP1-Pool_for_sle-15-x86_64'],
                                                 'repositoryid': 'Dev_Python_2_Module_15_SP1_x86_64_Python_2_Module_15_SP1_x86_64_SLE-Module-Python2-15-SP1-Pool_for_sle-15-x86_64'}]}}

        self.assertEqual(expected, report.content)

    @unittest.skipIf(YUM == False, "Yum not present")
    @patch('katello.enabled_report.yum.YumBase.conf')
    def test_var_interpolation_yum(self, yum_base_conf):
        yum_base_conf.yumvar = {'releasever': "6.22", 'basearch': "80286"}
        rh_repo = os.path.join(os.path.dirname(__file__), 'data/repos/redhat.repo.with_vars')
        report = enabled_report.EnabledReport(rh_repo)
        expected = {'enabled_repos': {'repos': [{'baseurl': ['https://enabled_repo.com/6.22/80286'], 'repositoryid': 'enabled_one'}]}}

        self.assertEqual(expected, report.content)
