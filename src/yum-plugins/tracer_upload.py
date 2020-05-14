import time

from katello.tracer import Query, upload_tracer_profile

from yum.plugins import TYPE_CORE, TYPE_INTERACTIVE

requires_api_version = '2.3'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)


def query_apps(conduit):
    """Returns all apps that need restarting """
    query = Query()

    # When running via yum we need to pass tracer a list of packages and
    # their last modified time so it has no need to access the rpmdb (which
    # would fail as yum has a lock on it)
    packages = []

    # Packages in the current transation
    pkgs = conduit.getTsInfo().getMembers()
    for pkg in pkgs:
        pkg.modified = time.time()
        packages.append(pkg)
    rpmdb = conduit.getRpmDB()  # All other packages
    for pkg in rpmdb:
        pkg.modified = pkg.installtime
        packages.append(pkg)
    return query.from_packages(packages).now().affected_applications().get()


def posttrans_hook(conduit):
    if not conduit.confBool("main", "supress_debug"):
        conduit.info(2, "Uploading Tracer Profile")
    try:
        upload_tracer_profile(query_apps, conduit)
    except:
        if not conduit.confBool("main", "supress_errors"):
            conduit.error(2, "Unable to upload Tracer Profile")
