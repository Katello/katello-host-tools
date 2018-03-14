import os

import dnf.cli

from dnfpluginscore import logger

from katello.repos import EnabledRepoCache, upload_enabled_repos_report
from katello.enabled_report import EnabledReport
from katello.constants import REPOSITORY_PATH

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
