#!/usr/bin/python
#
# Copyright 2017 ATIX AG
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

from os import readlink, getppid, environ
from os.path import basename
import sys
import logging

from katello.packages import upload_package_profile

from zypp_plugin import Plugin

class KatelloZyppPlugin(Plugin):

    def __init__(self):
        Plugin.__init__(self)
        self.num1 = self.num2 = None
        self.description = ""
        self.cleanup = "number"
        self.userdata = {}


    def parse_userdata(self, s):
        userdata = {}
        for kv in s.split(","):
            k, v = kv.split("=", 1)
            k = k.strip()
            if not k:
                raise ValueError
            userdata[k] = v.strip()
        return userdata


    def get_userdata(self, headers):
        try:
            return self.parse_userdata(headers['userdata'])
        except KeyError:
            pass
        except ValueError:
            logging.error("invalid userdata")
        return {}


    def PLUGINBEGIN(self, headers, body):
        self.description = "zypp(%s)" % basename(readlink("/proc/%d/exe" % getppid()))
        self.userdata = self.get_userdata(headers)
        self.ack()

    def PLUGINEND(self, headers, body):
        logging.info("Uploading Package Profile")
        try:
            upload_package_profile()
        except:
            logging.error("Unable to upload Package Profile")
        self.ack()


if __name__ == '__main__':
    if "DISABLE_KATELLO_ZYPP_PLUGIN" in environ:
        logging.info("$DISABLE_KATELLO_ZYPP_PLUGIN is set - disabling katello-zypp-plugin")

        # As the plugin is disabled, we are adding a dummy
        # Plugin so that zypper still works.
        plugin = Plugin()
    else:
        plugin = KatelloZyppPlugin()

    plugin.main()
