#
# Copyright 2014 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#

import dnf.cli

from dnfpluginscore import logger

from katello.packages import purge_package_cache, upload_package_profile


class PackageUploadCommand(dnf.cli.Command):
    aliases = ['katello-upload-packages']
    summary = 'Upload system package data to Katello'

    def configure(self):
        self.cli.demands.root_user = True  # needed to read consumer certs

    def run(self):
        if self.opts.forceupload:
            purge_package_cache()
        upload_package_profile()

    @staticmethod
    def set_argparser(parser):
        parser.add_argument("-f", "--forceupload",
                            help="Force package upload even if it does not seem out of date.",
                            action='store_true')


class PackageUpload(dnf.Plugin):
    name = 'package-upload'
    config_name = 'package_upload'

    def __init__(self, base, cli):
        super(PackageUpload, self).__init__(base, cli)
        if cli:
            cli.register_command(PackageUploadCommand)

    def transaction(self):
        conf = self.read_config(self.base.conf)
        enabled = (conf.has_section('main')
                   and conf.has_option('main', 'enabled')
                   and conf.getboolean('main', 'enabled'))

        if enabled:
            if (conf.has_option('main', 'supress_debug')
                    and not conf.getboolean('main', 'supress_debug')):
                logger.info("Uploading Package Profile")
            try:
                upload_package_profile()
            except Exception:
                if (conf.has_option('main', 'supress_errors')
                        and not conf.getboolean('main', 'supress_errors')):
                    logger.error("Unable to upload Package Profile")
