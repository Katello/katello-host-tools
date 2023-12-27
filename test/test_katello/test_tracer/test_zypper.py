import unittest
from katello.tracer.zypper import (
    execute_zypper_ps,
    collect_services_state,
    check_for_reboot_flag,
    ZypperTracerApp,
    collect_apps,
)

import subprocess

from mock import patch, Mock


class TestCheckForRebootFlag(unittest.TestCase):
    @patch("katello.tracer.zypper.path.isfile")
    def test_reboot_needed_flag(self, m):
        m.return_value = True
        apps = check_for_reboot_flag()
        self.assertEqual(type(apps), list)
        self.assertTrue(len(apps) == 1)
        self.assertIsInstance(apps[0], ZypperTracerApp)
        # Validate kernel
        self.assertEqual(apps[0].name, "kernel")
        self.assertEqual(apps[0].helper, "You will have to reboot your computer")
        self.assertEqual(apps[0].type, "static")

    @patch("katello.tracer.zypper.path.isfile")
    def test_not_reboot_needed_flag(self, m):
        m.return_value = False
        apps = check_for_reboot_flag()
        self.assertEqual(apps, [])


class TestExecuteZypperPs(unittest.TestCase):
    @patch.object(subprocess, "check_output")
    def test_execute_zypper_ps_output(self, m):
        zypper_ps_output = """
auditd
dbus
getty@tty1
haveged
systemd-logind"""
        output_list = zypper_ps_output.split("\n")
        m.return_value = zypper_ps_output
        self.assertEqual(execute_zypper_ps(), output_list)
        self.assertEqual(m.call_args.args, (["zypper", "ps", "-sss"],))
        self.assertEqual(m.call_args.kwargs, {"universal_newlines": True})
        self.assertEqual(len(collect_apps()), 5)


class TestCollectServicesState(unittest.TestCase):
    @patch("katello.tracer.zypper.execute_zypper_ps")
    def test_service_restart(self, m):
        output = ["systemd-logind"]
        m.return_value = output
        apps = collect_services_state()
        self.assertEqual(type(apps), list)
        self.assertTrue(len(apps) == 1)
        self.assertIsInstance(apps[0], ZypperTracerApp)
        # Validate service
        self.assertEqual(apps[0].name, "systemd-logind")
        self.assertEqual(apps[0].helper, "systemctl restart systemd-logind")
        self.assertEqual(apps[0].type, "daemon")

    @patch("katello.tracer.zypper.execute_zypper_ps")
    def test_no_service_restart_needed(self, m):
        output = []
        m.return_value = output
        apps = collect_services_state()
        self.assertEqual(type(apps), list)
        self.assertTrue(len(apps) == 0)


class TestCollectApps(unittest.TestCase):
    @patch("katello.tracer.zypper.collect_services_state")
    @patch("katello.tracer.zypper.check_for_reboot_flag")
    def test_collect_apps_reboot(self, m, p):
        expected_output = [] + [ZypperTracerApp("kernel", "You will have to reboot your computer", "static")]
        m.return_value = []
        p.return_value = [expected_output[0]]
        actual_output = collect_apps()
        self.assertEqual(type(actual_output), list)
        self.assertTrue(len(actual_output) == 1)
        self.assertEqual(actual_output[0], expected_output[0])


    @patch("katello.tracer.zypper.collect_services_state")
    @patch("katello.tracer.zypper.check_for_reboot_flag")
    def test_collect_apps_services(self, m, p):
        expected_output = [ZypperTracerApp("systemd-logind", "systemctl restart systemd-logind", "daemon")] + []
        m.return_value = [expected_output[0]]
        p.return_value = []
        actual_output = collect_apps()
        self.assertEqual(type(actual_output), list)
        self.assertTrue(len(actual_output) == 1)
        self.assertEqual(actual_output[0], expected_output[0])
