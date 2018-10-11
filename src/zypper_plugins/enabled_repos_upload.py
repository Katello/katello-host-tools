#!/usr/bin/env python
import sys
import logging, traceback

from katello.utils import plugin_enabled
from katello.constants import ENABLED_REPOS_PLUGIN_CONF
from katello.repos import upload_enabled_repos_report
from katello.enabled_report import EnabledReport
from zypp_plugin import Plugin

from katello.constants import ZYPPER_REPOSITORY_PATH

class EnabledReposUpload(Plugin):
    def __init__(self):
        Plugin.__init__(self)

    def PLUGINEND(self, headers, body):
        if plugin_enabled(ENABLED_REPOS_PLUGIN_CONF):
            logging.info("Uploading Enabled Repositories Report")
            try:
                report = EnabledReport(ZYPPER_REPOSITORY_PATH)
                logging.info("Uploading Enabled Repositories Report ->  %s" % str(report))
                upload_enabled_repos_report(report)
            except:
                logging.error("Unable to upload Enabled Repositories Report - %s" % traceback.format_exc())
        self.ack()

if __name__ == '__main__':
    plugin = EnabledReposUpload()
    plugin.main()
