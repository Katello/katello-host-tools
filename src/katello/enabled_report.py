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
        enabled_repos = [{"repositoryid": section,"baseurl": [self._replace_vars(config.get(section, "baseurl"))]} for section in enabled_sections]
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

    def _replace_vars(self, repo_url):
        """
        returns a string with "$basearch" and "$releasever" replaced.

        :param repo_url: a repo URL that you want to replace $basearch and $releasever in.
        :type path: str
        """
        mappings = self._obtain_mappings()
        return repo_url.replace('$releasever', mappings['releasever']).replace('$basearch', mappings['basearch'])

    def _obtain_mappings(self):
        """
        returns a hash with "basearch" and "releasever" set. This will try dnf first, and them yum if dnf is not installed.
        """
        try:
            return self._obtain_mappings_dnf()
        except ImportError:
            return self._obtain_mappings_yum()

    def _obtain_mappings_dnf(self):
        import dnf
        db = dnf.dnf.Base()
        return {'releasever': db.conf.substitutions['releasever'], 'basearch': db.conf.substitutions['basearch']}

    def _obtain_mappings_yum(self):
        import yum
        yb = yum.YumBase()
        return {'releasever': yb.conf.yumvar['releasever'], 'basearch': yb.conf.yumvar['basearch']}
