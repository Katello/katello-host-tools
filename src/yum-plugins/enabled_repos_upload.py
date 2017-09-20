import sys
import os
try:
    import json
except ImportError:
    import simplejson as json

from yum import YumBase
sys.path.append('/usr/share/rhsm')

from yum.plugins import TYPE_CORE, TYPE_INTERACTIVE

try:
    from subscription_manager.identity import ConsumerIdentity
except ImportError:
    from subscription_manager.certlib import ConsumerIdentity

from rhsm.connection import UEPConnection, RemoteServerException, GoneException

try:
    from subscription_manager.injectioninit import init_dep_injection
    init_dep_injection()
except ImportError:
    pass

requires_api_version = '2.3'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)

def upload_enabled_repos_report():
    path = '/etc/yum.repos.d/redhat.repo'
    uep = UEP()
    report = EnabledReport(path)
    content = report.content
    consumer_id = lookup_consumer_id()
    if consumer_id is None:
        error_message('Cannot upload enabled repos report, is this client registered?')
    else:
        cache = EnabledRepoCache(consumer_id, content)
        if not cache.is_valid():
            uep.report_enabled(consumer_id, content)
            cache.save()

def error_message(msg):
    sys.stderr.write(msg + "\n")

def lookup_consumer_id():
    try:
        certificate = ConsumerIdentity.read()
        return certificate.getConsumerId()
    except IOError:
        return None

class EnabledRepoCache:
    CACHE_FILE = '/var/cache/katello-agent/enabled_repos.json'
    def __init__(self, consumer_id, content):
        self.consumer_id = consumer_id
        self.content = content

    @staticmethod
    def remove_cache():
        try:
            os.remove(EnabledRepoCache.CACHE_FILE)
        except OSError:
            pass

    def is_valid(self):
        if not os.path.isfile(self.CACHE_FILE):
            return False
        file = open(self.CACHE_FILE)
        try:
            return self.data() == json.loads(file.read())
        except ValueError:
            return False

    def data(self):
        return {self.consumer_id: self.content}

    def save(self):
        file = open(self.CACHE_FILE, 'w')
        file.write(json.dumps(self.data()))
        file.close()

class UEP(UEPConnection):
    """
    Represents the UEP.
    """

    def __init__(self):
        key = ConsumerIdentity.keypath()
        cert = ConsumerIdentity.certpath()
        UEPConnection.__init__(self, key_file=key, cert_file=cert)

    def report_enabled(self, consumer_id, report):
        """
        Report enabled repositories to the UEP.
        :param consumer_id: The consumer ID.
        :type consumer_id: str
        :param report: The report to send.
        :type report: dict
        """
        method = '/systems/%s/enabled_repos' % self.sanitize(consumer_id)
        try:
            self.conn.request_put(method, report)
        except (RemoteServerException, GoneException), e:
            error_message(str(e))

class EnabledReport(object):
    """
    Represents the enabled repos report.
    @ivar content: The report content <dict>:
      - basearch <str>
      - releasever <str>
      - repos[] <dict>:
        - repositoryid <str>
        - baseurl <str>
    :type content: dict
    """

    @staticmethod
    def find_enabled(yb, repofn):
        """
        Get enabled repos part of the report.
        :param yb: yum lib.
        :type yb: YumBase
        :param repofn: The .repo file basename used to filter the report.
        :type repofn: str
        :return: The repo list content
        :rtype: dict
        """
        enabled = []
        for r in yb.repos.listEnabled():
            if not r.repofile:
                continue
            fn = os.path.basename(r.repofile)
            if fn != repofn:
                continue
            item = dict(repositoryid=r.id, baseurl=r.baseurl)
            enabled.append(item)
        return dict(repos=enabled)

    @staticmethod
    def generate(repofn):
        """
        Generate the report content.
        :param repofn: The .repo file basename used to filter the report.
        :type repofn: str
        :return: The report content
        :rtype: dict
        """
        yb = YumBase()
        try:
            return dict(enabled_repos=EnabledReport.find_enabled(yb, repofn))
        finally:
            yb.close()

    def __init__(self, path):
        """
        :param path: A .repo file path used to filter the report.
        :type path: str
        """
        self.content = EnabledReport.generate(os.path.basename(path))

    def __str__(self):
        return str(self.content)

def close_hook(conduit):
    if not conduit.confBool("main", "supress_debug"):
        conduit.info(2, "Uploading Enabled Repositories Report")
    try:
        upload_enabled_repos_report()
    except:
        if not conduit.confBool("main", "supress_errors"):
            conduit.error(2, "Unable to upload Enabled Repositories Report")

