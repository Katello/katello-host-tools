from __future__ import absolute_import
from os import path

# The file is created by /etc/kernel/postinst.d/unattended-upgrades (part of unattended-upgrades pkg)
REBOOT_NEEDED_FLAG = "/var/run/reboot-required"


class AptTracerApp:
    pass


def collect_apps(plugin=None):
    apps = []
    if path.isfile(REBOOT_NEEDED_FLAG):
        app = AptTracerApp()
        app.name = "kernel"
        app.helper = "You will have to reboot your computer"
        app.type = "static"
        apps.append(app)
    return apps
