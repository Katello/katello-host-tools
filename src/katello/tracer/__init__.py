from __future__ import absolute_import
from katello.uep import get_uep, lookup_consumer_id
import sys
import imp

def collect_apps():
    raise NotImplementedError("Couldn't detect package manager. Failed to query affected apps!")

# RHEL based systems
try:
    imp.find_module('dnf')
    from katello.tracer.dnf import collect_apps
except ImportError:
    try:
        imp.find_module('yum')
        from tracer.query import Query
        def collect_apps():
            query = Query()
            return query.affected_applications().get()
    except ImportError:
        pass

# debian based systems
try:
    imp.find_module('apt')
    from katello.tracer.deb import collect_apps
except ImportError:
    pass

# SUSE based systems
try:
    imp.find_module('zypp_plugin')
    from katello.tracer.zypper import collect_apps
except ImportError:
    pass

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
    return collect_apps()


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
