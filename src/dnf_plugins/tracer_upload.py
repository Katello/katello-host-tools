import dnf.cli

from dnfpluginscore import logger

from katello.tracer import query_affected_apps, upload_tracer_profile


class TracerUploadCommand(dnf.cli.Command):
    aliases = ['katello-tracer-upload']
    summary = 'Upload Tracer data to Katello'

    def configure(self):
        self.cli.demands.root_user = True

    def run(self):
        upload_tracer_profile(query_affected_apps, None)


class TracerUpload(dnf.Plugin):
    name = 'tracer-upload'
    config_name = 'tracer_upload'

    def __init__(self, base, cli):
        super(TracerUpload, self).__init__(base, cli)
        if cli:
            cli.register_command(TracerUploadCommand)

    def transaction(self):
        conf = self.read_config(self.base.conf)
        enabled = (conf.has_section('main') and
                   conf.has_option('main', 'enabled') and
                   conf.getboolean('main', 'enabled'))

        if enabled:
            if (conf.has_option('main', 'supress_debug') and not
               conf.getboolean('main', 'supress_debug')):
                logger.info("Uploading Tracer Profile")
            try:
                """
                Unlike yum, the transaction is already written to the DB
                by this point so we don't need to do any work to give Tracer
                a list of affected apps.
                """
                upload_tracer_profile(query_affected_apps, self)
            except Exception:
                if (conf.has_option('main', 'supress_errors') and not
                   conf.getboolean('main', 'supress_errors')):
                    logger.error("Unable to upload Tracer Profile")
