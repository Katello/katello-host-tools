import os
import sys
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/'))

from katello.agent.pulp import libdnf

@unittest.skipIf('dnf' not in sys.modules, "Dnf not present")
class TestLibDnf(unittest.TestCase):
  def test_package_update_on_advisories(self):
      advisories = set(["RHSA-1000"])
      packages = set([("foo","1.0"), ("bar","2.0")])

      def applicable_advisories(items):
        self.assertEqual(advisories, items.ids)
        return [(MagicMock(), packages)]

      mock_libdnf = MagicMock()
      mock_libdnf.__enter__ = lambda instance: instance
      mock_libdnf.applicable_advisories = applicable_advisories
      with patch('katello.agent.pulp.libdnf.LibDnf', return_value= mock_libdnf):
        package = libdnf.Package()
        package.update([],advisories)

        #strip the evrs out of the package
        packages = set([pack[0] for pack in packages])
        mock_libdnf.upgrade.assert_called_with(packages)
