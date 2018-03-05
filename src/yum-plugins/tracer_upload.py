import sys
import time

try:
  from tracer.query import Query
except ImportError:
  sys.exit('Error Importing tracer! Is tracer installed?')

from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE
from katello.tracer import upload_tracer_profile

requires_api_version = '2.3'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)

def query_apps(conduit):
    """Returns all apps that need restarting """
    query = Query()
    if conduit:
        # When running via yum we need to pass tracer a list of packages and 
        # their last modified time so it has no need to access the rpmdb (which
        # would fail as yum/dnf has a lock on it) 
        packages = []
        pkgs = conduit.getTsInfo().getMembers() # Packages in the current transation
        for pkg in pkgs:
            pkg.modified = time.time()
            packages.append(pkg)
        rpmdb = conduit.getRpmDB() # All other packages
        for pkg in rpmdb:
            pkg.modified = pkg.installtime
            packages.append(pkg)
        return query.from_packages(packages).now().affected_applications().get()
    else:
        return query.affected_applications().get()

def posttrans_hook(conduit):
    if not conduit.confBool("main", "supress_debug"):
        conduit.info(2, "Uploading Tracer Profile")
    try:
        upload_tracer_profile(query_apps, conduit)
    except:
        if not conduit.confBool("main", "supress_errors"):
            conduit.error(2, "Unable to upload Tracer Profile")
