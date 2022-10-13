from __future__ import absolute_import
from katello.uep import get_uep, lookup_consumer_id
import sys
import imp

def collect_apps():
    raise NotImplementedError("This is not the method you want to use. Normally, this method should be provided by deb_tracer or zypper_tracer")

try:
    imp.find_module('apt')
    from katello.deb_tracer import collect_apps
    apt = True
except ImportError as e:
    apt = False

try:
    imp.find_module('dnf')
    dnf = True
except ImportError:
    dnf = False

try:
    imp.find_module('yum')
    yum = True
except ImportError:
    yum = False

if yum or dnf:
    from tracer.query import Query

try:
    imp.find_module('zypp_plugin')
    from katello.zypper_tracer import collect_apps
    zypp = True
except ImportError:
    zypp = False


def upload_tracer_profile(queryfunc, plugin=None):
    uep = get_uep()
    consumer_id = lookup_consumer_id()
    if consumer_id is None:
        sys.stderr.write("Cannot upload tracer data, is this client registered?\n")
    else:
        method = '/consumers/%s/tracer' % uep.sanitize(consumer_id)
        data = {"traces": get_apps(queryfunc, plugin)}
        uep.conn.request_put(method, data)


def query_affected_apps(plugin=None):
    if yum or dnf:
        query = Query()
        return query.affected_applications().get()
    elif zypp or apt:
        return collect_apps()
    else:
        raise Exception("Couldn't detect package manager. Failed to query affected apps!")


def get_apps(queryfunc, plugin=None):
    """
    Return a array with nested arrays
    containing name, how to restart & app type
    for every package that needs restarting
    """
    apps = {}
    for app in queryfunc(plugin):
        apps[app.name] = {"helper": app.helper, "type": app.type}
    if plugin:
        # Don't report yum/dnf back if this if being ran via them.
        apps.pop("yum", None)
        apps.pop("dnf", None)
    return apps
