import os

import dnf.cli

from dnfpluginscore import logger

from katello.constants import REPOSITORY_PATH
from katello.repos import EnabledRepoCache, upload_enabled_repos_report


class UploadReposCommand(dnf.cli.Command):
    aliases = ['katello-upload-enabled-repos']
    summary = 'Upload enabled repository data to Katello'

    def configure(self):
        self.cli.demands.root_user = True

    def run(self):
        if self.opts.forceupload:
            EnabledRepoCache.remove_cache()
        report = EnabledReport(REPOSITORY_PATH)
        upload_enabled_repos_report(report)

    @staticmethod
    def set_argparser(parser):
        parser.add_argument("-f", "--forceupload",
                            help="Force enabled repository upload even if it does not seem out of date.",
                            action='store_true')


class EnabledReposUpload(dnf.Plugin):
    name = 'enabled-repos-upload'
    config_name = 'enabled_repos_upload'

    def __init__(self, base, cli):
        super(EnabledReposUpload, self).__init__(base, cli)
        if cli:
            cli.register_command(UploadReposCommand)

    def transaction(self):
        conf = self.read_config(self.base.conf)
        enabled = (conf.has_section('main')
                   and conf.has_option('main', 'enabled')
                   and conf.getboolean('main', 'enabled'))

        if enabled is True:
            if (conf.has_option('main', 'supress_debug') and not conf.getboolean('main', 'supress_debug')):
                logger.info("Uploading Enabled Repositories Report")
            try:
                report = EnabledReport(REPOSITORY_PATH)
                upload_enabled_repos_report(report)
            except:
                if (conf.has_option('main', 'supress_errors') and not conf.getboolean('main', 'supress_errors')):
                    logger.error("Unable to upload Enabled Repositories Report")


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
    def find_enabled(dnf_base, repofile):
        """
        Get enabled repos part of the report.
        :param dnf_base: dnf lib.
        :type dnf_base: dnf.Base
        :param repofile: The .repo file basename used to filter the report.
        :type repofile: str
        :return: The repo list content
        :rtype: dict
        """
        enabled = []
        dnf_base.read_all_repos()
        for repo in dnf_base.repos.iter_enabled():
            if not repo.repofile:
                continue
            if os.path.basename(repo.repofile) != repofile:
                continue
            item = {"repositoryid": repo.id, "baseurl": repo.baseurl}
            enabled.append(item)
        return {"repos": enabled}

    @staticmethod
    def generate(repofile):
        """
        Generate the report content.
        :param repofile: The .repo file basename used to filter the report.
        :type repofile: str
        :return: The report content
        :rtype: dict
        """
        base = dnf.Base()
        try:
            return {"enabled_repos": EnabledReport.find_enabled(base, repofile)}
        finally:
            base.close()

    def __init__(self, path):
        """
        :param path: A .repo file path used to filter the report.
        :type path: str
        """
        self.content = EnabledReport.generate(os.path.basename(path))

    def __str__(self):
        return str(self.content)
