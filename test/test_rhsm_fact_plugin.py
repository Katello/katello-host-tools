import os
import socket
import sys
from unittest import TestCase

from mock import Mock

sys.path.append(os.path.join(os.path.dirname(__file__), '../src/rhsm-plugins'))
from fqdn import FactsPlugin


class TestFactsPlugin(TestCase):
    FQDN_FACT = 'network.fqdn'

    def setUp(self):
        self.plugin = FactsPlugin(conf=True)
        self.conduit = Mock()
        self.conduit.facts = {}

    def test_facts_plugin_set_fqdn(self):
        self.conduit.facts[self.FQDN_FACT] = 'whatever.com'

        self.plugin.post_facts_collection_hook(self.conduit)

        assert self.conduit.facts[self.FQDN_FACT] == 'whatever.com'

    def test_facts_plugin_unset_fqdn(self):
        self.plugin.post_facts_collection_hook(self.conduit)

        assert self.conduit.facts['network.fqdn'] == socket.getfqdn()
