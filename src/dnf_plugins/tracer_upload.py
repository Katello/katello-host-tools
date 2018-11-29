import time

import dnf.cli

from dnfpluginscore import logger

from katello.tracer import upload_tracer_profile

from tracer import Package, Query


class TracerUploadCommand(dnf.cli.Command):
    aliases = ['katello-tracer-upload']
    summary = 'Upload Tracer data to Katello'

    def configure(self):
        self.cli.demands.root_user = True

    def run(self):
        upload_tracer_profile(query_apps, None)


class TracerUpload(dnf.Plugin):
    name = 'tracer-upload'
    config_name = 'tracer_upload'

    def __init__(self, base, cli):
        super(TracerUpload, self).__init__(base, cli)
        if cli:
            cli.register_command(TracerUploadCommand)

    def transaction(self):
        conf = self.read_config(self.base.conf)
        enabled = (conf.has_section('main')
                   and conf.has_option('main', 'enabled')
                   and conf.getboolean('main', 'enabled'))

        if enabled:
            if (conf.has_option('main', 'supress_debug') and not conf.getboolean('main', 'supress_debug')):
                logger.info("Uploading Tracer Profile")
            try:
                upload_tracer_profile(query_apps, self)
            except Exception:
                if (conf.has_option('main', 'supress_errors') and not conf.getboolean('main', 'supress_errors')):
                    logger.error("Unable to upload Tracer Profile")


def query_apps(plugin):
    query = Query()
    if plugin:
        packages = []
        iset = set(package.name for package in plugin.base.transaction.install_set)
        rset = set(package.name for package in plugin.base.transaction.remove_set)
        installed = set(package.name for package in plugin.base.sack.query().installed())

        # When running via dnf we need to pass tracer a list of packages and
        # their last modified time so it has no need to access the rpmdb (which
        # would fail as dnf has a lock on it)
        packages = [Package(p, time.time()) for p in (iset | rset | installed)]

        return query.from_packages(packages).now().affected_applications().get()

    return query.affected_applications().get()
