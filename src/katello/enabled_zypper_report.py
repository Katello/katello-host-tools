#!/usr/bin/python

import os
from katello.enabled_report import EnabledReport
from xml.dom import minidom

class EnabledZypperReport(EnabledReport):

    def __init__(self):
        self.content = self.__generate()

    def __generate(self):
        """
        returns a dict of all enabled_repos
        """

        stream = os.popen('zypper -x lr')
        output = stream.read()
        xmldoc = minidom.parseString(output)
        return {"enabled_repos": self.__parse_xml(xmldoc) }

    def __parse_xml(self, xmldoc):
        """
        returns a dict of enabled repositories

        :param xmldoc: a xml structure of repositories
        :type xmldoc: dom element
        """

        enabled_repos = []

        repos = xmldoc.getElementsByTagName("repo")
        for repo in repos:
            alias = repo.getAttribute("alias")
            enabled = repo.getAttribute("enabled")
            plain_url = repo.getElementsByTagName("url")[0].firstChild.data

            if enabled == '1':
                repoid = alias.replace('rhsm:', '')
                url = plain_url[:plain_url.find('?')]
                enabled_repos.append({"repositoryid": repoid, "baseurl": [url] })

        return {"repos": enabled_repos}
