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

from katello.packages import upload_package_profile

from yum.plugins import TYPE_CORE, TYPE_INTERACTIVE

requires_api_version = '2.3'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)


def posttrans_hook(conduit):
    if not conduit.confBool("main", "supress_debug"):
        conduit.info(2, "Uploading Package Profile")
    try:
        upload_package_profile()
    except:
        if not conduit.confBool("main", "supress_errors"):
            conduit.error(2, "Unable to upload Package Profile")
