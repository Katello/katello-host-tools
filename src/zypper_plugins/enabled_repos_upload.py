#!/usr/bin/python
import sys
import logging, traceback

from katello.repos import upload_enabled_repos_report
from katello.utils import combined_profiles_enabled
from katello.enabled_report import EnabledReport
from zypp_plugin import Plugin

from katello.constants import ZYPPER_REPOSITORY_PATH

class EnabledReposUpload(Plugin):
    def __init__(self):
        Plugin.__init__(self)

    def PLUGINEND(self, headers, body):
        logging.info("Uploading Enabled Repositories Report")
        try:
            report = None
            if not combined_profiles_enabled():
                report = EnabledReport(ZYPPER_REPOSITORY_PATH)
            logging.info("Uploading Enabled Repositories Report ->  %s" % str(report))
            upload_enabled_repos_report(report)
        except:
            logging.error("Unable to upload Enabled Repositories Report - %s" % traceback.format_exc())
        self.ack()

if __name__ == '__main__':
    plugin = EnabledReposUpload()
    plugin.main()
