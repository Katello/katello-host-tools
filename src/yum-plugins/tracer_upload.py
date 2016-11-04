import sys
import json
import httplib
import time

try:
  from tracer.query import Query
except ImportError:
  sys.exit('Error Importing tracer! Is tracer installed?')

from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE
from rhsm.config import RhsmConfigParser, initConfig

sys.path.append('/usr/share/rhsm')
from subscription_manager.identity import ConsumerIdentity

requires_api_version = '2.3'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)

def query_apps(conduit):
    """Returns all apps that need restarting """
    query = Query()
    if conduit:
        pkgs = conduit.getTsInfo().getMembers()
        packages = []
        for pkg in pkgs:
            pkg.modified = time.time()
            packages.append(pkg)
        return query.from_packages(packages).now().affected_applications().get()
    else:
        return query.affected_applications().get()

def get_apps(conduit):
    """
    Return a array with nested arrays 
    containing name, how to restart & app type
    for every package that needs restarting
    """   
    apps = {}
    for app in query_apps(conduit):
        apps[app.name] = { "helper": app.helper, "type": app.type}
    if conduit: 
        #Don't report yum/dnf back if this if being ran via them.
        apps.pop("yum", None)
        apps.pop("dnf", None)
    return apps

def upload_tracer_profile(conduit=False):
    data =  json.dumps({ "traces": get_apps(conduit) })
    headers = { "Content-type": "application/json" }

    conn = httplib.HTTPSConnection(
            RhsmConfigParser.get(initConfig() ,'server', 'hostname'),
            RhsmConfigParser.get(initConfig() ,'server', 'port'),
            key_file = ConsumerIdentity.keypath(),
            cert_file = ConsumerIdentity.certpath()
           )
    conn.request('PUT', '/rhsm/consumers/%s/tracer' % (ConsumerIdentity.read().getConsumerId()), data, headers=headers)
    response = conn.getresponse()

def posttrans_hook(conduit):
    conduit.info(2, "Uploading Tracer Profile")
    try:
        upload_tracer_profile(conduit)
    except:
        conduit.error(2, "Unable to upload Tracer Profile")
