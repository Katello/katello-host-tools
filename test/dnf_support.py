from configparser import ConfigParser
from unittest import TestCase

import dnf.cli.option_parser

from mock import Mock


# https://github.com/rpm-software-management/dnf-plugins-core/blob/master/tests/support.py
def configure_command(cmd, args):
    parser = dnf.cli.option_parser.OptionParser()
    args = [cmd._basecmd] + args
    parser.parse_main_args(args)
    parser.parse_command_args(cmd, args)
    return cmd.configure()


class PluginTestCase(TestCase):
    def setUp(self):
        self.parser = ConfigParser()
        self.base = Mock()
        self.base.conf = dnf.conf.Conf()
        self.cli = Mock()
