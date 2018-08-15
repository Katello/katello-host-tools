import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))

try:
    from katello.agent.pulp import libyum
except ImportError:
    print("Yum wasn't present")


@unittest.skipIf('yum' not in sys.modules, "Yum not present")
class TestLibYum(unittest.TestCase):
    def test_register_command(self):
        lib = libyum.LibYum()
        assert lib.registerCommand(True)


class TestPackage(unittest.TestCase):
    def setUp(self):
        self.package = libyum.Package(commit=False)

    def test_install_nevra(self):
        pattern = libyum.Pattern('walrus', '*', '0.71', '1', 'noarch')
        assert self.package.install([pattern])

    def test_install_nevra_name(self):
        pattern = libyum.Pattern('walrus-0.71-1.noarch')
        assert self.package.install([pattern])
