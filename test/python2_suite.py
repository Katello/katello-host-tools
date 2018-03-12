import sys
import unittest

modules = [
    'test_katello.test_repos',
    'test_katello.test_plugin',
    'test_rhsm_fact_plugin',
    'test_yum_plugins.test_enabled_repos_upload',
]

map(__import__, modules)

suite = unittest.TestSuite()
for module in [sys.modules[modname] for modname in modules]:
    suite.addTest(unittest.TestLoader().loadTestsFromModule(module))

unittest.TextTestRunner(verbosity=2).run(suite)
