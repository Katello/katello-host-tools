from os import path;

class EnabledReport(object):
    def __str__(self):
        return str(self.content)

    @classmethod
    def factory(cls):
        if path.exists('/usr/bin/yum'):
            from katello.enabled_yum_report import EnabledYumReport
            report = EnabledYumReport()
        elif path.exists('/usr/bin/zypper'):
            from katello.enabled_zypper_report import EnabledZypperReport
            report = EnabledZypperReport()
        else:
            raise ImportError('Neither yum nor zypper is installed')

        return report
