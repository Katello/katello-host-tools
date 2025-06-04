import unittest
from katello.tracer.deb import (
    needrestart,
    has_needrestart,
    use_flag,
    use_needrestart,
    AptTracerApp,
    collect_apps
)
import subprocess

from mock import patch


class TestNeedrestart(unittest.TestCase):

    @patch.object(subprocess, "check_output")
    def test_needrestart_output(self, m):
        needrestart_output = """
NEEDRESTART-VER: 3.5
NEEDRESTART-KCUR: 5.10.0-7-amd64
NEEDRESTART-KEXP: 5.10.0-10-amd64
NEEDRESTART-KSTA: 3
NEEDRESTART-SVC: cron.service
NEEDRESTART-SVC: dbus.service
NEEDRESTART-SVC: getty@tty1.service
NEEDRESTART-SVC: ifup@ens160.service
NEEDRESTART-SVC: rsyslog.service
NEEDRESTART-SVC: ssh.service
NEEDRESTART-SVC: systemd-journald.service
NEEDRESTART-SVC: systemd-logind.service
NEEDRESTART-SVC: systemd-timesyncd.service
NEEDRESTART-SVC: unattended-upgrades.service
NEEDRESTART-SVC: user@0.service """

        output_list = needrestart_output.split("\n")
        m.return_value = needrestart_output
        self.assertEqual(needrestart(), output_list)
        expected_args = (["needrestart", "-b"],)
        expected_kwargs = {"universal_newlines": True}
        self.assertEqual(m.call_args, (expected_args, expected_kwargs))
        self.assertEqual(len(collect_apps()), 12)

    @patch.object(subprocess, "check_output")
    def test_needrestart_exception_file_not_found(self, m):
        m.side_effect = OSError()
        with self.assertRaises(SystemExit) as cm:
            needrestart()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 'Please install needrestart')


class TestCollectApps(unittest.TestCase):
    @patch("katello.tracer.deb.which")
    def test_has_needrestart_not_python3(self, m):
        m.return_value = None
        self.assertEqual(has_needrestart(), False)
        self.assertEqual(m.call_args.args, ("needrestart",))

    @patch("katello.tracer.deb.which")
    def test_has_needrestart_ok_python3(self, m):
        m.return_value = "/usr/sbin/needrestart"
        self.assertEqual(has_needrestart(), True)
        self.assertEqual(m.call_args.args, ("needrestart",))


class TestUseFlag(unittest.TestCase):
    @patch("katello.tracer.deb.path.isfile")
    def test_reboot_needed_flag(self, m):
        m.return_value = True
        apps = use_flag()
        self.assertEqual(type(apps), list)
        self.assertTrue(len(apps) == 1)
        self.assertIsInstance(apps[0], AptTracerApp)
        # Validate kernel
        self.assertEqual(apps[0].name, "kernel")
        self.assertEqual(apps[0].helper, "You will have to reboot your computer")
        self.assertEqual(apps[0].type, "static")

    @patch("katello.tracer.deb.path.isfile")
    def test_not_reboot_needed_flag(self, m):
        m.return_value = False
        apps = use_flag()
        self.assertEqual(apps, [])


class TestUseNeedRestart(unittest.TestCase):
    @patch("katello.tracer.deb.needrestart")
    def test_system_reboot(self, m):
        output = [
            "NEEDRESTART-VER: 3.5",
            "NEEDRESTART-KCUR: 5.10.0-7-amd64",
            "NEEDRESTART-KEXP: 5.10.0-10-amd64",
            "NEEDRESTART-KSTA: 3"
        ]
        m.return_value = output
        apps = use_needrestart()
        self.assertEqual(type(apps), list)
        self.assertTrue(len(apps) == 1)
        # Validate kernel
        self.assertIsInstance(apps[0], AptTracerApp)
        self.assertEqual(apps[0].name, "kernel")
        self.assertEqual(apps[0].helper, "Please restart your system")
        self.assertEqual(apps[0].type, "static")

    @patch("katello.tracer.deb.needrestart")
    def test_service_restart(self, m):
        output = [
            "NEEDRESTART-VER: 3.5",
            "NEEDRESTART-KCUR: 5.10.0-7-amd64",
            "NEEDRESTART-KEXP: 5.10.0-10-amd64",
            "NEEDRESTART-SVC: systemd-logind.service",
        ]
        m.return_value = output
        apps = use_needrestart()
        self.assertEqual(type(apps), list)
        self.assertTrue(len(apps) == 1)
        self.assertIsInstance(apps[0], AptTracerApp)
        # Validate service
        self.assertEqual(apps[0].name, "systemd-logind")
        self.assertEqual(apps[0].helper, "systemctl restart systemd-logind")
        self.assertEqual(apps[0].type, "daemon")

    @patch("katello.tracer.deb.needrestart")
    def test_service_and_system_restart(self, m):
        output = [
            "NEEDRESTART-VER: 3.5",
            "NEEDRESTART-KCUR: 5.10.0-7-amd64",
            "NEEDRESTART-KEXP: 5.10.0-10-amd64",
            "NEEDRESTART-KSTA: 3",
            "NEEDRESTART-SVC: systemd-logind.service",
        ]
        m.return_value = output
        apps = use_needrestart()
        self.assertEqual(type(apps), list)
        self.assertTrue(len(apps) == 2)
        self.assertIsInstance(apps[1], AptTracerApp)
        # Validate service
        self.assertEqual(apps[1].name, "systemd-logind")
        self.assertEqual(apps[1].helper, "systemctl restart systemd-logind")
        self.assertEqual(apps[1].type, "daemon")
        # Validate kernel
        self.assertEqual(apps[0].name, "kernel")
        self.assertEqual(apps[0].helper, "Please restart your system")
        self.assertEqual(apps[0].type, "static")

    @patch("katello.tracer.deb.needrestart")
    def test_no_restart_needed(self, m):
        output = [
            "NEEDRESTART-VER: 3.5",
            "NEEDRESTART-KCUR: 5.10.0-7-amd64",
            "NEEDRESTART-KEXP: 5.10.0-10-amd64",
            "NEEDRESTART-KSTA: 1"
        ]
        m.return_value = output
        apps = use_needrestart()
        self.assertEqual(apps, [])
