import logging

import dnf
import libdnf
import hawkey


from gettext import gettext as _

from dnf.exceptions import CompsError


log = logging.getLogger('__file__')


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


class TransactionReport(object):
    """
    DNF transaction report.
    """

    def __init__(self, transaction):
        """
        Args:
            transaction: A DNF transaction.
        """

        ACTION_STATES = [
            dnf.transaction.PKG_INSTALL,
            dnf.transaction.PKG_REMOVE,
            dnf.transaction.PKG_UPGRADE
        ]
        FAILED_STATES = [
            libdnf.transaction.TransactionItemState_ERROR,
            libdnf.transaction.TransactionItemState_UNKNOWN
        ]

        self.resolved = []
        self.failed = []
        for item in transaction:
            po = item.pkg
            if po and item.state in FAILED_STATES:
                _list = self.failed
            elif po and item.action in ACTION_STATES:
                _list = self.resolved
            else:
                continue

            package = dict(
                qname=str(po),
                repoid=po.repoid,
                name=po.name,
                version=po.version,
                release=po.release,
                arch=po.arch,
                epoch=po.epoch)
            _list.append(package)

    def dict(self):
        """
        Dictionary representation.

        Returns:
            dict: self
        """
        return {
            'resolved': self.resolved,
            'failed': self.failed,
            'deps': [],
        }

    def log(self, heading):
        """
        Log the report.

        Args:
            heading (str): Log entry heading.
        """
        if not self:
            return
        names = [p['qname'] for p in self.resolved]
        _list = ''.join(['\n  {}'.format(n) for n in names])
        if _list:
            log.info(heading.format(_list))

    def __len__(self):
        return len(self.resolved)


class InstallTxReport(TransactionReport):
    """
    Install transaction report.
    """

    HEADING = _('\nInstalled:{}')

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

    HEADING = _('\nUpdated:{}')

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

    HEADING = _('\nErased:{}')

    def log(self, heading=HEADING):
        """
        Log the report.

        Args:
            heading (str): Log entry heading.
        """
        super(EraseTxReport, self).log(heading)


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
        with LibDnf() as lib:
            lib.install(str(p) for p in patterns)
            if self.commit:
                lib.do_transaction()
            report = InstallTxReport(lib.transaction)
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
        with LibDnf() as lib:
            patterns = set(str(p) for p in patterns)
            if advisories:
                for ad, packages in lib.applicable_advisories(AdvisoryFilter(ids=advisories)):
                    for name, evr in packages:
                        patterns.add(name + '-' + evr)
                if patterns:
                   lib.upgrade(patterns)
            else:
                lib.upgrade(patterns)
            if self.commit:
                lib.do_transaction()
            report = UpdateTxReport(lib.transaction or ())
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
        with LibDnf() as lib:
            lib.remove(str(p) for p in patterns)
            if self.commit:
                lib.do_transaction()
            report = EraseTxReport(lib.transaction)
            if self.commit:
                report.log()
        return report.dict()


class PackageGroup(API):
    """
    Package group management API.
    """

    @staticmethod
    def _resolved(lib, names):
        """
        Resolve group names to IDs.

        Args:
            lib (LibDnf): An opened lib.
            names (collections.Iterable): A list of group names.

        Yields:
            Group IDs.

        Raises:
            CompsError: When name cannot be resolved.
        """
        for p in names:
            group = lib.comps.group_by_pattern(p)
            if not group:
                raise CompsError(_('Group "{g}" not found.').format(g=p))
            else:
                yield group.id

    def install(self, names):
        """
        Install package groups.

        Args:
            names (collections.Iterable): A list of group names.

        Returns:
            dict: A dictionary representation of a TransactionReport.
        """
        with LibDnf() as lib:
            lib.group_install(self._resolved(lib, names))
            if self.commit:
                lib.do_transaction()
            report = InstallTxReport(lib.transaction)
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
        with LibDnf() as lib:
            lib.group_remove(self._resolved(lib, names))
            if self.commit:
                lib.do_transaction()
            report = EraseTxReport(lib.transaction)
            if self.commit:
                report.log()
        return report.dict()


class AdvisoryFilter(object):
    """
    Advisory filter.

    Filter by advisory IDs and/or types.
    """

    LABEL2TYPE = {
        _('BUGFIX'): hawkey.ADVISORY_BUGFIX,
        _('ENHANCEMENT'): hawkey.ADVISORY_ENHANCEMENT,
        _('SECURITY'): hawkey.ADVISORY_SECURITY,
        _('UNKNOWN'): hawkey.ADVISORY_UNKNOWN,
    }

    def __init__(self, ids=(), types=()):
        """
        Args:
            ids (collections.Iterable): List of advisory IDs.
            types (collections.Iterable): List of advisory types.  See: LABEL2TYPE.
        """
        self.ids = {s.upper() for s in ids}
        self.types = {self.LABEL2TYPE.get(s.upper(), hawkey.ADVISORY_UNKNOWN) for s in types}

    def match(self, advisory):
        """
        Match advisory.

        Args:
            advisory: An advisory.

        Returns:
            bool: True when matched.
        """
        if self.ids and (advisory.id.upper() not in self.ids):
            return False
        if self.types and (advisory.type not in self.types):
            return False
        return True


class LibDnf(dnf.Base):
    """
    DNF base.

    Notes:
        Requires dnf >= 2.7.5
    """

    # Logging cannot be reconfigured.
    # Plugins cannot be reloaded within the process.
    __lib_loaded = False

    def __init__(self):
        """
        Initialization.
        """
        super(LibDnf, self).__init__()
        self.conf.assumeyes = True
        self.conf.substitutions.update_from_etc("/")

    def open(self):
        """
        Open the lib.
        """
        self.read_all_repos()
        if not LibDnf.__lib_loaded:
            self._logging._setup_from_dnf_conf(self.conf)
            self.init_plugins()
            LibDnf.__lib_loaded = True
        self.fill_sack('auto', True)
        self._plugins.run_sack()
        self.read_comps()

    def install(self, patterns):
        """
        Install packages specified by the patterns.

        Args:
            patterns: List of (str) patterns.

        Notes:
            Need to call do_transaction() to commit the changes.
        """
        for p in patterns:
            super(LibDnf, self).install(p)
        self.resolve(allow_erasing=False)
        self._plugins.run_resolved()
        self._download()

    def upgrade(self, patterns=()):
        """
        Upgrade packages specified by the patterns.

        Args:
            patterns: List of (str) patterns.

        Notes:
            Need to call do_transaction() to commit the changes.
        """
        if patterns:
            for p in patterns:
                super(LibDnf, self).upgrade(p)
        else:
            self.upgrade_all()
        self.resolve(allow_erasing=False)
        self._plugins.run_resolved()
        self._download()

    def remove(self, patterns):
        """
        Remove packages specified by the patterns.

        Args:
            patterns: List of (str) patterns.

        Notes:
            Need to call do_transaction() to commit the changes.
        """
        for p in patterns:
            super(LibDnf, self).remove(p)
        self.resolve(allow_erasing=False)
        self._plugins.run_resolved()

    def group_install(self, grp_ids):
        """
        Install package groups.

        Args:
            grp_ids: List of (str) group IDs.

        Notes:
            Need to call do_transaction() to commit the changes.
        """
        for grp_id in grp_ids:
            super(LibDnf, self).group_install(grp_id, ('mandatory', 'default'))
        self.resolve(allow_erasing=False)
        self._plugins.run_resolved()
        self._download()

    def group_remove(self, grp_ids):
        """
        Remove package groups.

        Args:
            grp_ids: List of (str) group IDs.

        Notes:
            Need to call do_transaction() to commit the changes.
        """
        for grp_id in grp_ids:
            super(LibDnf, self).group_remove(grp_id)
        self.resolve(allow_erasing=False)
        self._plugins.run_resolved()

    def list_advisories(self, filter=AdvisoryFilter()):
        """
        Get a list of advisories matching the filter.

        Args:
            filter (AdvisoryFilter): An optional filter.

        Returns:
            list: The list of matching advisories.
        """
        advisories = []
        query = self.sack.query().filter(upgradable=True)
        for package in query.installed():
            for ad in package.get_advisories(hawkey.GT):
                if filter.match(ad):
                    advisories.append(ad)
        return advisories

    def applicable_advisories(self, filter=AdvisoryFilter()):
        """
        Get a list of applicable advisories matching the filter.

        Args:
            filter (AdvisoryFilter): An optional filter.

        Returns:
            list: The list of applicable advisories.
        """
        advisories = []
        query = self.sack.query()
        installed = {(p.name, p.arch): p for p in query.installed()}
        for ad in self.list_advisories(filter):
            packages = set()
            for ap in ad.packages:
                try:
                    ip = installed[(ap.name, ap.arch)]
                except KeyError:
                    continue
                if self.sack.evr_cmp(ip.evr, ap.evr) < 0:
                    packages.add((ap.name, ap.evr))
            if packages:
                advisories.append((ad, packages))
        return advisories

    def _download(self):
        """
        Download packages as needed.
        """
        self.download_packages(self.transaction.install_set)

    def __enter__(self):
        super(LibDnf, self).__enter__()
        self.open()
        return self
