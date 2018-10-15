import os.path
from ConfigParser import ConfigParser
from katello.constants import REPOSITORY_PATH
import yum


class EnabledReport(object):
    def __generate(self):
        if not os.path.exists(self.repofile):
            return {"enabled_repos": {"repos": []}}

        config = ConfigParser()
        config.read(self.repofile)
        enabled_sections = [section for section in config.sections() if config.getboolean(section, "enabled")]
        enabled_repos = [{"repositoryid": section, "baseurl": [self._replace_vars(config.get(section, "baseurl"))]} for section in enabled_sections]
        return {"enabled_repos": {"repos": enabled_repos}}

    def __init__(self, repo_file=REPOSITORY_PATH):
        """
        :param path: A .repo file path used to filter the report.
        :type path: str
        """
        self.yb = yum.YumBase()
        self.repofile = repo_file
        self.content = self.__generate()

    def __str__(self):
        return str(self.content)

    def _replace_vars(self, repo_url):
        """
        returns a string with "$basearch" and "$releasever" replaced.

        :param repo_url: a repo URL that you want to replace $basearch and $releasever in.
        :type path: str
        """
        mappings = {'releasever': self.yb.conf.yumvar['releasever'], 'basearch': self.yb.conf.yumvar['basearch']}

        return repo_url.replace('$releasever', mappings['releasever']).replace('$basearch', mappings['basearch'])
