#!/usr/bin/env python

import sys

import unittest2 as unittest


if sys.version_info[0] == 2:
    modules = [
        'test_katello.test_enabled_report',
        'test_katello.test_packages',
        'test_katello.test_repos',
        'test_katello.test_utils'
    ]

    try:
        import zypp_plugin
        zypper_enabled = True
    except ImportError:
        zypper_enabled = False

    if zypper_enabled:
        modules.append('zypper_plugins.test_enabled_repos_upload')
        modules.append('zypper_plugins.test_package_upload')
        modules.append('zypper_plugins.test_tracer_upload')
        modules.append('test_katello.test_tracer')
        modules.append('test_katello.test_tracer.test_zypper')
    else:
        modules.append('test_yum_plugins.test_enabled_repos_upload')

        if sys.version_info[1] > 6:
            modules.append('test_katello.test_tracer')
            modules.append('test_katello.test_tracer.test_deb')

    map(__import__, modules)

    suite = unittest.TestSuite()
    for module in [sys.modules[modname] for modname in modules]:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(module))
else:
    suite = unittest.defaultTestLoader.discover('test')

result = unittest.TextTestRunner(verbosity=2).run(suite)

sys.exit(not result.wasSuccessful())
