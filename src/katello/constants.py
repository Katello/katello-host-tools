import imp

ENABLED_REPOS_CACHE_FILE = '/var/cache/katello-agent/enabled_repos.json'
PACKAGE_CACHE_FILE = '/var/lib/rhsm/packages/packages.json'
REPOSITORY_PATH = '/etc/yum.repos.d/redhat.repo'
ZYPPER_REPOSITORY_PATH = '/etc/rhsm/zypper.repos.d/redhat.repo'

PACKAGE_PROFILE_PLUGIN_CONF = '/etc/yum/pluginconf.d/package_upload.conf'
ENABLED_REPOS_PLUGIN_CONF = '/etc/yum/pluginconf.d/enabled_repos_upload.conf'

DISABLE_PACKAGE_PROFILE_VAR = 'DISABLE_KATELLO_PACKAGE_PROFILE'
DISABLE_ENABLE_REPOS_VAR = 'DISABLE_KATELLO_ENABLED_REPOS'
PROFILE_CACHE_FILE = '/var/lib/rhsm/cache/profile.json'

try:
    imp.find_module('zypp_plugin')
    ZYPPER = True
except ImportError:
    ZYPPER = False

try:
    imp.find_module('yum')
    YUM = True
except ImportError:
    YUM = False
