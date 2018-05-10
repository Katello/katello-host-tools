import sys
import unittest2 as unittest

if sys.version_info[0] == 2:
    modules = [
        'test_katello.test_enabled_report',
        'test_katello.test_packages',
        'test_katello.test_repos',
        'test_rhsm_fact_plugin',
        'test_yum_plugins.test_enabled_repos_upload',
        'zypper_plugins.test_enabled_repos_upload'
    ]

    if sys.version_info[1] > 6:
        modules.append('test_katello.test_plugin')

    map(__import__, modules)

    suite = unittest.TestSuite()
    for module in [sys.modules[modname] for modname in modules]:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(module))
else:
    suite = unittest.defaultTestLoader.discover('test')

result = unittest.TextTestRunner(verbosity=2).run(suite)

sys.exit(not result.wasSuccessful())
