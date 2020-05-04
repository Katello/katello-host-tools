import six
import logging

from itertools import chain
from gettext import gettext as _
from optparse import OptionParser

from yum import YumBase
from yum.plugins import TYPE_CORE, TYPE_INTERACTIVE
from yum.Errors import InstallError
from yum import constants
from yum import updateinfo


log = logging.getLogger(__name__)
logfile = logging.getLogger('yum.filelogging')


class Pattern(object):
    """
    Package matching pattern.

    Attributes:
        name (str): Name.
        epoch (str): Epoch.
        version (str): Version.
        release (str): Release.
        arch (str) Arch..
    """

    __slots__ = (
        'name',
        'epoch',
        'version',
        'release',
        'arch',
    )

    FIELDS = (
        ('epoch', ('', ':')),
        ('name', ('', '')),
        ('version', ('-', '')),
        ('release', ('-', '')),
        ('arch', ('.', '')),
    )

    def __init__(self, name, epoch='', version='', release='', arch=''):
        """
        NEVRA

        Args:
            name (str): Name.
            epoch (str): Epoch.
            version (str): Version.
            release (str): Release.
            arch (str) Arch.
        """
        self.name = name
        self.epoch = epoch
        self.version = version
        self.release = release
        self.arch = arch

    def __eq__(self, other):
       return str(self) == str(other)

    def __str__(self):
        pattern = []
        for name, sep in self.FIELDS:
            value = getattr(self, name)
            if not value:
                continue
            if sep[0]:
                pattern.append(sep[0])
            pattern.append(value)
            if sep[1]:
                pattern.append(sep[1])
        return ''.join(pattern)


class TransactionReport(object):
    """
    YUM transaction report.
    """

    def __init__(self, ts_info, states):
        """
        Args:
            ts_info: A YUM transaction.
            states: List of package states to be included.
        """
        self.deps = []
        self.resolved = []
        self.failed = []
        for t in ts_info:
            if t.output_state not in states:
                continue
            qname = str(t.po)
            package = dict(
                qname=qname,
                repoid=t.repoid,
                name=t.po.name,
                version=t.po.ver,
                release=t.po.rel,
                arch=t.po.arch,
                epoch=t.po.epoch)
            if t.output_state == constants.TS_FAILED:
                self.failed.append(package)
            if t.isDep:
                self.deps.append(package)
            else:
                self.resolved.append(package)

    def dict(self):
        """
        Dictionary representation.

        Returns:
            dict: self
        """
        return {
            'resolved': self.resolved,
            'failed': self.failed,
            'deps': self.deps,
        }

    def log(self, heading):
        """
        Log the report.

        Args:
            heading (str): Log entry heading.
        """
        if not self:
            return
        for qname in [p['qname'] for p in chain(self.resolved, self.deps)]:
            entry = heading.format(qname)
            logfile.info(entry)
            log.info(entry)

    def __len__(self):
        return len(self.resolved) + len(self.deps)


class InstallTxReport(TransactionReport):
    """
    Install transaction report.
    """

    HEADING = _('Installed: {}')

    STATES = (
        constants.TS_FAILED,
        constants.TS_INSTALL,
        constants.TS_TRUEINSTALL,
        constants.TS_UPDATE
    )

    def __init__(self, ts_info, states=STATES):
        """
        Args:
            ts_info: A YUM transaction.
            states: List of package states to be included.
        """
        super(InstallTxReport, self).__init__(ts_info, states)

    def log(self, heading=HEADING):
        """
        Log the report.

        Args:
            heading (str): Log entry heading.
        """
        super(InstallTxReport, self).log(heading)


class UpdateTxReport(TransactionReport):
    """
    Update transaction report.
    """

    HEADING = _('Updated: {}')

    STATES = (
        constants.TS_FAILED,
        constants.TS_INSTALL,
        constants.TS_TRUEINSTALL,
        constants.TS_UPDATE
    )

    def __init__(self, ts_info, states=STATES):
        """
        Args:
            ts_info: A YUM transaction.
            states: List of package states to be included.
        """
        super(UpdateTxReport, self).__init__(ts_info, states)

    def log(self, heading=HEADING):
        """
        Log the report.

        Args:
            heading (str): Log entry heading.
        """
        super(UpdateTxReport, self).log(heading)


class EraseTxReport(TransactionReport):
    """
    Erase transaction report.
    """

    HEADING = _('Erased: {}')

    STATES = (
        constants.TS_FAILED,
        constants.TS_ERASE
    )

    def __init__(self, ts_info, states=STATES):
        """
        Args:
            ts_info: A YUM transaction.
            states: List of package states to be included.
        """
        super(EraseTxReport, self).__init__(ts_info, states)

    def log(self, heading=HEADING):
        """
        Log the report.

        Args:
            heading (str): Log entry heading.
        """
        super(EraseTxReport, self).log(heading)


class API(object):
    """
    Abstract package management API.

    Attributes:
        commit (bool): Commit the transaction.
    """

    def __init__(self, commit=True):
        """
        Args:
            commit (bool): Commit the transaction.
                Use False for a "dry run".
        """
        self.commit = commit


class Package(API):
    """
    The package management API.
    """

    def install(self, patterns):
        """
        Install packages.

        Args:
            patterns (collections.Iterable): A list of Pattern.

        Returns:
            dict: A dictionary representation of a TransactionReport.
        """
        with LibYum() as lib:
            for pattern in patterns:
                try:
                    lib.install(pattern=str(pattern))
                except InstallError as caught:
                    description = six.text_type(caught).encode('utf-8')
                    caught.value = '%s: %s' % (pattern, description)
                    raise caught
            lib.resolveDeps()
            if self.commit and len(lib.tsInfo):
                lib.processTransaction()
            report = InstallTxReport(lib.tsInfo)
            if self.commit:
                report.log()
            return report.dict()

    def update(self, patterns=(), advisories=()):
        """
        Update packages.

        Args:
            patterns (collections.Iterable): A list of Pattern.
            advisories (collections.Iterable): A list of advisory IDs.

        Returns:
            dict: A dictionary representation of a TransactionReport.
        """
        with LibYum() as lib:
            if advisories:
                lib.updateinfo_filters = {
                    'bzs': [],
                    'bugfix': None,
                    'sevs': [],
                    'security': None,
                    'advs': advisories,
                    'cves': []
                }
                updateinfo.update_minimal(lib)
            else:
                if patterns:
                    for pattern in patterns:
                        lib.update(pattern=str(pattern))
                else:
                    lib.update()
            lib.resolveDeps()
            if self.commit and len(lib.tsInfo):
                lib.processTransaction()
            report = UpdateTxReport(lib.tsInfo)
            if self.commit:
                report.log()
            return report.dict()

    def uninstall(self, patterns):
        """
        Uninstall (remove) packages.

        Args:
            patterns (collections.Iterable): A list of Pattern.

        Returns:
            dict: A dictionary representation of a TransactionReport.
        """
        with LibYum() as lib:
            for pattern in patterns:
                lib.remove(pattern=str(pattern))
            lib.resolveDeps()
            if self.commit and len(lib.tsInfo):
                lib.processTransaction()
            report = EraseTxReport(lib.tsInfo)
            if self.commit:
                report.log()
            return report.dict()


class PackageGroup(API):
    """
    Package group management API.
    """

    def install(self, names):
        """
        Install package groups.

        Args:
            names (collections.Iterable): A list of group names.

        Returns:
            dict: A dictionary representation of a TransactionReport.
        """
        with LibYum() as lib:
            for name in names:
                lib.selectGroup(name)
            lib.resolveDeps()
            if self.commit and len(lib.tsInfo):
                lib.processTransaction()
            report = InstallTxReport(lib.tsInfo)
            if self.commit:
                report.log()
            return report.dict()

    def uninstall(self, names):
        """
        Uninstall package groups.

        Args:
            names (collections.Iterable): A list of group names.

        Returns:
            dict: A dictionary representation of a TransactionReport.
        """
        with LibYum() as lib:
            for name in names:
                lib.groupRemove(name)
            lib.resolveDeps()
            if self.commit and len(lib.tsInfo):
                lib.processTransaction()
            report = EraseTxReport(lib.tsInfo)
            if self.commit:
                report.log()
            return report.dict()


class LibYum(YumBase):
    """
    A YUM base.
    """

    def __init__(self):
        """
        Initialization.
        """
        parser = OptionParser()
        parser.parse_args([])
        self.__parser = parser
        super(LibYum, self).__init__()
        self.preconf.optparser = self.__parser
        self.preconf.plugin_types = (TYPE_CORE, TYPE_INTERACTIVE)
        self.conf.assumeyes = True


    """
    Plugins ordinarily used via CLI may use YumBaseCli to register their respective commands
    Since we extend YumBase we need to make sure any such plugins we've loaded don't raise an error when doing so
    """
    def registerCommand(self, command):
      return self


    def doPluginSetup(self, *args, **kwargs):
        """
        Plugin setup.

        Args:
            *args:
            **kwargs:
        """
        super(LibYum, self).doPluginSetup(*args, **kwargs)
        p = self.__parser
        options, args = p.parse_args([])
        self.plugins.setCmdLine(options, args)

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.close()
