#
# Copyright 2014 Red Hat, Inc.
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

import sys
import os
sys.path.append('/usr/share/rhsm')

from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE

try:
  from subscription_manager import action_client
except ImportError:
  from subscription_manager import certmgr

try:
  from subscription_manager.identity import ConsumerIdentity
except ImportError:
  from subscription_manager.certlib import ConsumerIdentity

from rhsm import connection

try:
    from subscription_manager.injectioninit import init_dep_injection
    init_dep_injection()
except ImportError:
    pass

CACHE_FILE = '/var/lib/rhsm/packages/packages.json'

requires_api_version = '2.3'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)

def remove_cache():
    try:
        os.remove(CACHE_FILE)
    except OSError:
        pass

def upload_package_profile():
    uep = connection.UEPConnection(cert_file=ConsumerIdentity.certpath(),
                                   key_file=ConsumerIdentity.keypath())
    get_manager().profilelib._do_update()

def get_manager():
    if 'subscription_manager.action_client' in sys.modules:
        mgr = action_client.ActionClient()
    else:
        # for compatability with subscription-manager > =1.13
        uep = connection.UEPConnection(cert_file=ConsumerIdentity.certpath(),
                                        key_file=ConsumerIdentity.keypath())
        mgr = certmgr.CertManager(uep=uep)
    return mgr

def posttrans_hook(conduit):
    conduit.info(2, "Uploading Package Profile")
    try:
        upload_package_profile()
    except:
        conduit.error(2, "Unable to upload Package Profile")

