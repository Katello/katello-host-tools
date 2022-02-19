#!/usr/bin/python

import optparse

from katello.constants import (DISABLE_ENABLE_REPOS_VAR, DISABLE_PACKAGE_PROFILE_VAR,
        ENABLED_REPOS_PLUGIN_CONF, PACKAGE_PROFILE_PLUGIN_CONF, REPOSITORY_PATH, YUM, ZYPPER,
        ZYPPER_REPOSITORY_PATH)
from katello.enabled_report import EnabledReport
from katello.packages import purge_package_cache, upload_package_profile
from katello.repos import EnabledRepoCache, upload_enabled_repos_report
from katello.utils import combined_profiles_enabled


def enabled_repos_upload():
    description = 'This report can be disabled by either disabling the package management plugin in ' +\
              ENABLED_REPOS_PLUGIN_CONF + ' or via the environment variable ' + DISABLE_ENABLE_REPOS_VAR
    parser = optparse.OptionParser(description=description)
    parser.add_option('-f', '--force', action='store_true',
            help="Force enabled repository upload even if it does not seem out of date, or is otherwise disabled..")
    (options, args) = parser.parse_args()
    if options.force:
        EnabledRepoCache.remove_cache()

    report = None
    if not combined_profiles_enabled():
        if YUM:
            repo_path = REPOSITORY_PATH
        elif ZYPPER:
            repo_path = ZYPPER_REPOSITORY_PATH
        else:
            raise IOError('Neither yum nor zypper can be used')
        report = EnabledReport(repo_path)

    upload_enabled_repos_report(report, options.force)


def package_upload():
    description = 'This report can be disabled by either disabling the package management plugin in ' + \
              PACKAGE_PROFILE_PLUGIN_CONF + ' or via the environment variable ' + DISABLE_PACKAGE_PROFILE_VAR
    parser = optparse.OptionParser(description=description)
    parser.add_option('-f', '--force', action='store_true',
            help="Force package upload even if it does not seem out of date.")

    (options, args) = parser.parse_args()
    if options.force:
        purge_package_cache()
    upload_package_profile(options.force)


def tracer_upload():
    try:
        from katello import tracer
    except ImportError:
        raise SystemExit('Tracer is not supported on your platform')
    else:
        tracer.upload_tracer_profile(tracer.query_affected_apps, None)
