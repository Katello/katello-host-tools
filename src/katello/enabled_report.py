import os.path, sys
from katello.constants import REPOSITORY_PATH
if sys.version_info[0] == 3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser

class EnabledReport(object):
    def __generate(self):
        if not os.path.exists(self.repofile):
            return {"enabled_repos": {"repos":[]}}

        config = ConfigParser()
        config.read(self.repofile)
        enabled_sections = [section for section in config.sections() if config.getboolean(section, "enabled")]
        enabled_repos = [{"repositoryid": section,"baseurl": config.get(section, "baseurl")} for section in enabled_sections]
        return {"enabled_repos": {"repos": enabled_repos}}

    def __init__(self, repo_file = REPOSITORY_PATH):
        """
        :param path: A .repo file path used to filter the report.
        :type path: str
        """
        self.repofile = repo_file
        self.content = self.__generate()

    def __str__(self):
        return str(self.content)
