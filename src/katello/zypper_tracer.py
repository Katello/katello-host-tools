from __future__ import absolute_import
from os import path

# The path is defined in zypper, see https://github.com/openSUSE/libzypp/blob/master/zypp/target/TargetImpl.cc
REBOOT_NEEDED_FLAG = "/var/run/reboot-needed"


class ZypperTracerApp:
    pass


def collect_apps(plugin=None):
    apps = []
    if path.isfile(REBOOT_NEEDED_FLAG):
        app = ZypperTracerApp()
        app.name = "kernel"
        app.helper = "You will have to reboot your computer"
        app.type = "static"
        apps.append(app)
    return apps
