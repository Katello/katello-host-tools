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
