from __future__ import absolute_import
from os import path
import subprocess

# The path is defined in zypper, see https://github.com/openSUSE/libzypp/blob/master/zypp/target/TargetImpl.cc
REBOOT_NEEDED_FLAG = "/var/run/reboot-needed"


class ZypperTracerApp:
    def __init__(self, name, helper, type):
        self.name = name
        self.helper = helper
        self.type = type


def check_for_reboot_flag():
    apps = []
    if path.isfile(REBOOT_NEEDED_FLAG):
        app = ZypperTracerApp("kernel", "You will have to reboot your computer", "static")
        apps.append(app)
    return apps


def execute_zypper_ps():
    output = subprocess.check_output(["zypper", "ps", "-sss"], universal_newlines=True)
    return output.split("\n")


def collect_services_state():
    apps = []
    output = execute_zypper_ps()
    for service in output:
        if service:
            app = ZypperTracerApp(service, "systemctl restart " + service, "systemd")
            apps.append(app)
    return apps


def collect_apps(plugin=None):
    apps = collect_services_state()
    reboot = check_for_reboot_flag()
    return apps + reboot
