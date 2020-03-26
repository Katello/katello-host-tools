import os.path
from katello.utils import ConfigParser
from katello.constants import REPOSITORY_PATH, YUM, ZYPPER

if YUM:
    import yum

class EnabledReport(object):
    def __generate(self):
        if not os.path.exists(self.repofile):
            return {"enabled_repos": {"repos": []}}

        config = ConfigParser()
        config.read(self.repofile)
        enabled_sections = [section for section in config.sections() if config.getboolean(section, "enabled")]
        enabled_repos = [{"repositoryid": section, "baseurl": [self._format_str(config.get(section, "baseurl"))]} for section in enabled_sections]
        return {"enabled_repos": {"repos": enabled_repos}}

    def __init__(self, repo_file=REPOSITORY_PATH):
        """
        :param path: A .repo file path used to filter the report.
        :type path: str
        """
        if YUM:
            self.yb = yum.YumBase()
            self.yb.preconf.debuglevel = 0
        self.repofile = repo_file
        self.content = self.__generate()

    def __str__(self):
        return str(self.content)

    def _format_str(self, repo_url):
        """
        returns a formatted string

        :param repo_url: a repo URL that you want to format
        :type path: str
        """

        if YUM:
            return self._replace_vars(repo_url)
        elif ZYPPER:
            return self._cut_question_mark(repo_url)
        else:
            return repo_url;

    def _cut_question_mark(self, repo_url):
        """
        returns a string where everything after the first occurence of ? is truncated

        :param repo_url: a repo URL that you want to modify
        :type path: str
        """
        return repo_url[:repo_url.find('?')]

    def _replace_vars(self, repo_url):
        """
        returns a string with "$basearch" and "$releasever" replaced.

        :param repo_url: a repo URL that you want to replace $basearch and $releasever in.
        :type path: str
        """

        mappings = {'releasever': self.yb.conf.yumvar['releasever'], 'basearch': self.yb.conf.yumvar['basearch']}

        return repo_url.replace('$releasever', mappings['releasever']).replace('$basearch', mappings['basearch'])
