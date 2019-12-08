#
# Copyright 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#

"""
The katello virtual agent.
Provides content management APIs for pulp within the RHSM environment.
"""
import os
import sys

sys.path.append('/usr/share/rhsm')

from time import sleep
from logging import getLogger
from subprocess import Popen

from six.moves import http_client as http

from gofer.decorators import load, unload, remote, action, FORK
from gofer.agent.plugin import Plugin
from gofer.pmon import PathMonitor
from gofer.config import Config

try:
    from subscription_manager.identity import ConsumerIdentity
except ImportError:
    from subscription_manager.certlib import ConsumerIdentity

from rhsm.connection import UEPConnection, RemoteServerException, GoneException

from katello.agent.pulp import Dispatcher


# This plugin
plugin = Plugin.find(__name__)

# Path monitoring
path_monitor = None

# Track registration status
registered = False


log = getLogger(__name__)


RHSM_CONFIG_PATH = '/etc/rhsm/rhsm.conf'


@load
def plugin_loaded():
    """
    Initialize the plugin.
    Called (once) immediately after the plugin is loaded.
     - setup path monitoring.
     - validate registration.  If registered:
       - setup plugin configuration.
    """
    global path_monitor
    path = ConsumerIdentity.certpath()
    path_monitor = PathMonitor()
    path_monitor.add(path, certificate_changed)
    path_monitor.start()
    while True:
        try:
            validate_registration()
            if registered:
                update_settings()
            # DONE
            break
        except Exception as e:
            log.warn(str(e))
            sleep(60)


@unload
def plugin_unloaded():
    """
    The plugin has been uploaded.
    """
    path_monitor.abort()


def bundle(certificate):
    """
    Bundle the key and cert and write to a file.
    :param certificate: A consumer identity certificate.
    :type certificate: ConsumerIdentity
    :return: The path to written bundle.
    :rtype: str
    """
    path = os.path.join(certificate.PATH, 'bundle.pem')
    fp = open(path, 'w')
    try:
        fp.write(certificate.key)
        fp.write(certificate.cert)
        return path
    finally:
        fp.close()


def certificate_changed(path):
    """
    A certificate change has been detected.
    On registration: setup the plugin; attach to the message broker.
    On un-registration: detach from the message broker.
    :param path: The path to the file that changed.
    :type path: str
    """
    log.info('changed: %s', path)
    while True:
        try:
            validate_registration()
            if registered:
                update_settings()
                plugin.attach()
            else:
                plugin.detach()
            # DONE
            break
        except Exception as e:
            log.warn(str(e))
            sleep(60)


def update_settings():
    """
    Setup the plugin based on the RHSM configuration.
    """
    rhsm_conf = Config(RHSM_CONFIG_PATH)
    certificate = ConsumerIdentity.read()
    if 'ca_cert_dir' in rhsm_conf['rhsm']:
        ca_cert_dir = rhsm_conf['rhsm']['ca_cert_dir']
    else:
        #handle old subscription-manager configurations
        ca_cert_dir = rhsm_conf['server']['ca_cert_dir']

    # the 'katello-default-ca.pem' is the ca used for generating the CA certs.
    # the 'candlepin-local.pem' is there for compatibility reasons (the old path where the
    # legacy installer was putting this file. If none of them is present, there is still
    # a chance the rhsm_conf['rhsm']['repo_ca_cert'] is serving as the CA for issuing
    # the client certs
    ca_candidates = [os.path.join(ca_cert_dir, 'katello-default-ca.pem'),
                     os.path.join(ca_cert_dir, 'candlepin-local.pem'),
                     rhsm_conf['rhsm']['repo_ca_cert'] % {'ca_cert_dir': ca_cert_dir}]
    existing_ca_certs = [cert for cert in ca_candidates if os.path.exists(cert)]
    if not existing_ca_certs:
       log.warn('None of the ca cert files %s found for the qpid connection' % ca_candidates)

       raise
    else:
       log.info('Using %s as the ca cert for qpid connection' % existing_ca_certs[0])

    plugin.cfg.messaging.cacert = existing_ca_certs[0]
    plugin.cfg.messaging.url = 'proton+amqps://%s:5647' % rhsm_conf['server']['hostname']
    plugin.cfg.model.queue = 'pulp.agent.%s' % certificate.getConsumerId()
    bundle(certificate)


def validate_registration():
    """
    Validate consumer registration by making a REST call
    to the server.  Updates the global 'registered' variable.
    """
    global registered
    registered = False

    if ConsumerIdentity.existsAndValid():
        consumer = ConsumerIdentity.read()
        consumer_id = consumer.getConsumerId()
    else:
        return

    try:
        uep = UEP()
        consumer = uep.getConsumer(consumer_id)
        registered = (consumer is not None)
    except GoneException:
        registered = False
    except RemoteServerException as e:
        if e.code not in (http.NOT_FOUND, http.GONE):
            log.warn(str(e))
            raise
    except Exception as e:
        log.exception(str(e))
        raise


class AgentRestart(object):
    """
    Restart the daemon after RPM upgrade.
    The %post in the RPM will write the RESTART_FILE.  The recurring
    'apply' action notices file and restarts the goferd service only when
    this plugin is not longer busy.
    """

    COMMAND = 'service goferd restart'
    RESTART_FILE = '/tmp/katello-agent-restart'

    @staticmethod
    def is_busy():
        """
        Determine if this plugin is busy by counting the pending
        requests in the persistent queue.

        :return: True if busy.
        :rtype: bool
        """
        pending = plugin.scheduler.pending
        path = os.path.join(pending.PENDING, pending.stream)
        count = len(os.listdir(path))
        return count > 0

    @staticmethod
    def restart():
        """
        Restart the goferd service.
          1. Delete the RESTART_FILE.
          2. Restart

        :return: The restart command exit value.
        :rtype: int
        """
        os.unlink(AgentRestart.RESTART_FILE)
        p = Popen(AgentRestart.COMMAND, shell=True)
        return p.wait()

    @action(minutes=3)
    def apply(self):
        """
        Detect the RESTART_FILE and restart the goferd service
        only when this plugin is not longer busy.  This ensures that
        an RPM update has completed.
        """
        if not os.path.exists(AgentRestart.RESTART_FILE):
            return
        if self.is_busy():
            return
        log.info('Restarting goferd.')
        exit_val = self.restart()
        # only reached when restart failed.
        log.error('Restart failed, exit=%d', exit_val)


class UEP(UEPConnection):
    """
    Represents the UEP.
    """

    def __init__(self):
        key = ConsumerIdentity.keypath()
        cert = ConsumerIdentity.certpath()
        UEPConnection.__init__(self, key_file=key, cert_file=cert)


# --- API --------------------------------------------------------------------
class Consumer(object):
    """
    When a consumer is unregistered, Katello notifies the goferd.
    """

    @remote
    def unregister(self):
        log.info('Consumer has been unregistered. '
                 'Katello agent will no longer function until '
                 'this system is reregistered.')


class Content(object):
    """
    Pulp Content Management.
    """

    @remote(model=FORK)
    def install(self, units, options):
        """
        Install the specified content units using the specified options.
        Delegated to content handlers.
        :param units: A list of content units to be installed.
        :type units: list of:
            { type_id:<str>, unit_key:<dict> }
        :param options: Install options; based on unit type.
        :type options: dict
        :return: A dispatch report.
        :rtype: DispatchReport
        """
        dispatcher = Dispatcher()
        report = dispatcher.install(units, options)
        return report.dict()

    @remote(model=FORK)
    def update(self, units, options):
        """
        Update the specified content units using the specified options.
        Delegated to content handlers.
        :param units: A list of content units to be updated.
        :type units: list of:
            { type_id:<str>, unit_key:<dict> }
        :param options: Update options; based on unit type.
        :type options: dict
        :return: A dispatch report.
        :rtype: DispatchReport
        """
        dispatcher = Dispatcher()
        report = dispatcher.update(units, options)
        return report.dict()

    @remote(model=FORK)
    def uninstall(self, units, options):
        """
        Uninstall the specified content units using the specified options.
        Delegated to content handlers.
        :param units: A list of content units to be uninstalled.
        :type units: list of:
            { type_id:<str>, unit_key:<dict> }
        :param options: Uninstall options; based on unit type.
        :type options: dict
        :return: A dispatch report.
        :rtype: DispatchReport
        """
        dispatcher = Dispatcher()
        report = dispatcher.uninstall( units, options)
        return report.dict()
