#!/usr/bin/python
#
# Copyright 2021 ATIX AG
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should

from os import path, environ
import logging
from katello.tracer import upload_tracer_profile


# The file is created by /etc/kernel/postinst.d/unattended-upgrades (part of unattended-upgrades pkg)
REBOOT_NEEDED_FLAG = "/var/run/reboot-required"

class TracerApp:
    pass

class TracerUpload:
    def collect_apps(self, _plugin):
        apps = []
        if path.isfile(REBOOT_NEEDED_FLAG):
            app = TracerApp()
            app.name = "kernel"
            app.helper = "You will have to reboot your computer"
            app.type = "static"
            apps.append(app)
        return apps

    def send(self):
        logging.info("Uploading Tracer Profile")
        try:
            upload_tracer_profile(self.collect_apps)
        except:
            logging.error("Unable to upload Tracer Profile")

if __name__ == '__main__':
    if "DISABLE_TRACER_UPLOAD_PLUGIN" in environ:
        logging.info("$DISABLE_TRACER_UPLOAD_PLUGIN is set - disabling katello tracer upload plugin")
    else:
        tracer = TracerUpload()
        tracer.send()

