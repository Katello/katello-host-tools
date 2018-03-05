import os
from yum import YumBase
from yum.plugins import TYPE_CORE, TYPE_INTERACTIVE

from katello.constants import REPOSITORY_PATH
from katello.repos import upload_enabled_repos_report

from logging import Logger

requires_api_version = '2.3'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)

class Yum(YumBase):
    """
    Provides custom configured yum object.
    """

    def cleanLoggers(self):
        """
        Clean handlers leaked by yum.
        """
        for n, lg in Logger.manager.loggerDict.items():
            if not n.startswith('yum.'):
                continue
            for h in lg.handlers:
                lg.removeHandler(h)

    def close(self):
        """
        This should be handled by __del__() but YumBase
        objects never seem to completely go out of scope and
        garbage collected.
        """
        YumBase.close(self)
        self.closeRpmDB()
        self.cleanLoggers()

class EnabledReport(object):
    """
    Represents the enabled repos report.
    @ivar content: The report content <dict>:
      - basearch <str>
      - releasever <str>
      - repos[] <dict>:
        - repositoryid <str>
        - baseurl <str>
    :type content: dict
    """

    @staticmethod
    def find_enabled(yb, repofn):
        """
        Get enabled repos part of the report.
        :param yb: yum lib.
        :type yb: YumBase
        :param repofn: The .repo file basename used to filter the report.
        :type repofn: str
        :return: The repo list content
        :rtype: dict
        """
        enabled = []
        for r in yb.repos.listEnabled():
            if not r.repofile:
                continue
            fn = os.path.basename(r.repofile)
            if fn != repofn:
                continue
            item = dict(repositoryid=r.id, baseurl=r.baseurl)
            enabled.append(item)
        return dict(repos=enabled)

    @staticmethod
    def generate(repofn):
        """
        Generate the report content.
        :param repofn: The .repo file basename used to filter the report.
        :type repofn: str
        :return: The report content
        :rtype: dict
        """
        yb = Yum()
        try:
            return dict(enabled_repos=EnabledReport.find_enabled(yb, repofn))
        finally:
            yb.close()

    def __init__(self, path):
        """
        :param path: A .repo file path used to filter the report.
        :type path: str
        """
        self.content = EnabledReport.generate(os.path.basename(path))

    def __str__(self):
        return str(self.content)

def close_hook(conduit):
    if not conduit.confBool("main", "supress_debug"):
        conduit.info(2, "Uploading Enabled Repositories Report")
    try:
	report = EnabledReport(REPOSITORY_PATH)
	upload_enabled_repos_report(report)
    except:
        if not conduit.confBool("main", "supress_errors"):
            conduit.error(2, "Unable to upload Enabled Repositories Report")
