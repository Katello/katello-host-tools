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
import httplib

sys.path.append('/usr/share/rhsm')

from time import sleep
from logging import getLogger
from subprocess import Popen

from katello.constants import REPOSITORY_PATH
from katello.repos import upload_enabled_repos_report
from katello.enabled_report import EnabledReport

from gofer.decorators import load, unload, remote, action
from gofer.agent.plugin import Plugin
from gofer.pmon import PathMonitor
from gofer.agent.rmi import Context
from gofer.config import Config


try:
    from subscription_manager.identity import ConsumerIdentity
except ImportError:
    from subscription_manager.certlib import ConsumerIdentity

from rhsm.connection import UEPConnection, RemoteServerException, GoneException

from pulp.agent.lib.dispatcher import Dispatcher
from pulp.agent.lib.conduit import Conduit as HandlerConduit


# This plugin
plugin = Plugin.find(__name__)

# Path monitoring
path_monitor = PathMonitor()

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
    path_monitor.add(REPOSITORY_PATH, send_enabled_report)
    path_monitor.start()
    while True:
        try:
            validate_registration()
            if registered:
                update_settings()
            # DONE
            break
        except Exception, e:
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
                send_enabled_report()
                plugin.attach()
            else:
                plugin.detach()
            # DONE
            break
        except Exception, e:
            log.warn(str(e))
            sleep(60)

def send_enabled_report(path=REPOSITORY_PATH):
    report = EnabledReport(path)
    upload_enabled_repos_report(report)

def update_settings():
    """
    Setup the plugin based on the RHSM configuration.
    """
    rhsm_conf = Config(RHSM_CONFIG_PATH)
    certificate = ConsumerIdentity.read()
    if rhsm_conf['rhsm'].has_key('ca_cert_dir'):
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
    plugin.cfg.messaging.uuid = 'pulp.agent.%s' % certificate.getConsumerId()
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
    except RemoteServerException, e:
        if e.code not in (httplib.NOT_FOUND, httplib.GONE):
            log.warn(str(e))
            raise
    except Exception, e:
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


class Conduit(HandlerConduit):
    """
    Provides integration between the gofer and pulp agent handler frameworks.
    """

    @property
    def consumer_id(self):
        """
        Get the current consumer ID
        :return: The unique consumer ID of the currently running agent
        :rtype:  str
        """
        certificate = ConsumerIdentity.read()
        return certificate.getConsumerId()

    def update_progress(self, report):
        """
        This method inentionally left blank mitigate Qpid journal
        latency related to AMQP 1.0.  The latency significantly
        degrades performance. If a better solution is found we
        may re-enable this method to actually report back progress.
        See http://projects.theforeman.org/issues/12375
        :param report: A handler progress report.
        :type report: object
        """

    def cancelled(self):
        """
        Get whether the current operation has been cancelled.
        :return: True if cancelled, else False.
        :rtype: bool
        """
        context = Context.current()
        return context.cancelled()

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
        log.info('Consumer has been unregistered. Katello agent will no longer function until this system is reregistered.')


class Content(object):
    """
    Pulp Content Management.
    """

    @remote
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
        conduit = Conduit()
        dispatcher = Dispatcher()
        report = dispatcher.install(conduit, units, options)
        return report.dict()

    @remote
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
        conduit = Conduit()
        dispatcher = Dispatcher()
        report = dispatcher.update(conduit, units, options)
        return report.dict()

    @remote
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
        conduit = Conduit()
        dispatcher = Dispatcher()
        report = dispatcher.uninstall(conduit, units, options)
        return report.dict()
