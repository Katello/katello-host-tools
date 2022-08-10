from __future__ import absolute_import
from os import path
import subprocess
import sys
try:
    from shutil import which
except ImportError:  # on Python 2
    from distutils.spawn import find_executable as which

# The file is created by /etc/kernel/postinst.d/unattended-upgrades (part of unattended-upgrades pkg)
REBOOT_NEEDED_FLAG = "/var/run/reboot-required"


class AptTracerApp:
    def __init__(self, name, helper, type):
        self.name = name
        self.helper = helper
        self.type = type


def has_needrestart():
    return which("needrestart") is not None


def use_flag():
    apps = []
    if path.isfile(REBOOT_NEEDED_FLAG):
        app = AptTracerApp("kernel", "You will have to reboot your computer", "static")
        apps.append(app)
    return apps


def needrestart():
    try:
        output = subprocess.check_output(["needrestart", "-b"], universal_newlines=True)
        return output.split("\n")
    except OSError:
        raise SystemExit("Please install needrestart")


def use_needrestart():
    apps = []
    services = []
    ksta = None
    output = needrestart()
    for item in output:
        output = item.split(":")
        if output[0] == "NEEDRESTART-KSTA":
            ksta = int(output[1])
        elif output[0] == "NEEDRESTART-SVC":
            services.append(output[1].replace(".service", "").strip())

    if ksta in (2, 3):
        app = AptTracerApp("kernel", "Please restart your system", "static")
        apps.append(app)

    for service in services:
        app = AptTracerApp(service, "systemctl restart " + service, "systemd")
        apps.append(app)

    return apps


def collect_apps(plugin=None):
    if has_needrestart:
        apps = use_needrestart()
    else:
        apps = use_flag()
    return apps
