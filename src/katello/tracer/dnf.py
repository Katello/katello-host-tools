import os
import re
import subprocess
import psutil
from katello.tracer.SystemdDbus import SystemdDbus

# these services need a reboot of the system
STATIC_SERVICES = [
    "systemd",
    "dbus",
]

# these apps are ignored and no tracer will be added
IGNORE_APPS = [
    "sudo",
    "su",
    "(sd-pam)",
]

REBOOT_HELPER= 'You will have to reboot your computer'
SESSION_HELPER = 'You will have to log out & log in again'

class DnfTracerApp:
    def __init__(self, name, helper, app_type):
        self.name = name
        self.helper = helper
        self.type = app_type


class Process:
    def __init__(self, bus, pid):
        self.bus = bus
        self.pid = int(pid)
        self.process = psutil.Process(self.pid)
        self.name = self.detect_name()

        # special handling for ssh sessions. Thanks to
        # https://github.com/FrostyX/tracer/blob/ff8fc924fcbe2f638dd88b50549813dab2b8595b/tracer/resources/processes.py#L79
        try:
            if self.name == 'sshd':
                exe = self.process.exe()
                cmdline = self.process.cmdline()
                if exe not in cmdline and len(cmdline) > 1:
                    self.name = 'ssh-{0}-session'.format(re.split(' |@',' '.join(cmdline))[1])
        except psutil.AccessDenied:
            pass

    def detect_name(self):
        if self.pid and self.bus.unit_path_from_pid(self.pid):
            if not self.bus.has_service_property_from_pid(self.pid, 'PAMName'):
                unit_id = self.bus.get_unit_property_from_pid(self.pid, 'Id')
                if unit_id and unit_id.endswith('.service'):
                    return unit_id[:-8]
        return self.process.name()

    def is_session(self):
        if self.name.startswith("ssh-") and self.name.endswith("-session"):
            return True

        terminal = self.process.terminal()
        if terminal is not None:
            parent = self.process.parent()
            if parent is None or terminal != parent.terminal():
                return True
        return False

    def is_reboot_required(self):
        return self.name in STATIC_SERVICES


def collect_services_state():
    env = dict(os.environ, LANG='C')
    process = subprocess.run(['dnf', 'needs-restarting'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if process.returncode != 0:
        return []

    lines = process.stdout.split('\n')
    pids = [line.split(' : ')[0].strip() for line in lines if ' : ' in line]

    apps = set()
    bus = SystemdDbus()
    added_services = []

    for pid in pids:
        p = Process(bus, pid)

        if p.name in IGNORE_APPS:
            continue

        app_type = 'daemon'
        helper = "systemctl restart " + p.name
        if p.is_session():
            app_type = 'session'
            helper = SESSION_HELPER
        if p.is_reboot_required():
            app_type = 'static'
            helper = REBOOT_HELPER

        if p.name is not None and p.name not in added_services:
            app = DnfTracerApp(p.name, helper, app_type)
            apps.add(app)
            added_services.append(p.name)
    return list(apps)


def collect_restart():
    apps = []
    process = subprocess.run(["dnf", "needs-restarting", "-r"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.returncode == 1:
        app = DnfTracerApp("kernel", REBOOT_HELPER, "static")
        apps.append(app)
    return apps


def collect_apps(plugin=None):
    apps = collect_services_state()
    reboot = collect_restart()
    return apps + reboot
