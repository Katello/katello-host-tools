from __future__ import absolute_import


from logging import getLogger

from katello.agent.pulp.report import ContentReport

try:
    from .libdnf import Package, PackageGroup, Pattern
except ImportError:
    from .libyum import Package, PackageGroup, Pattern


log = getLogger(__name__)


class ContentHandler(object):
    """
    <Abstract> Content handler.
    Defines the interface for handlers designed to implement CONTENT management requests.
    """

    def install(self, units, options):
        """
        Install content.

        Args:
            units (collections.Iterable): Content to be installed.
            options (dict): Handler specific options.

        Returns:
            DispatchReport: A report.

        Notes:
            Unit is: {type_id:<str>, unit_key:<dict>}
        """
        raise NotImplementedError()

    def update(self, units, options):
        """
        Update content.

        Args:
            units (collections.Iterable): Content to be updated.
            options (dict): Handler specific options.

        Returns:
            DispatchReport: A report.

        Notes:
            Unit is: {type_id:<str>, unit_key:<dict>}
        """
        raise NotImplementedError()

    def uninstall(self, units, options):
        """
        Uninstall content.

        Args:
            units (collections.Iterable): Content to be uninstalled.
            options (dict): Handler specific options.

        Returns:
            DispatchReport: A report.

        Notes:
            Unit is: {type_id:<str>, unit_key:<dict>}
        """
        raise NotImplementedError()


class PackageReport(ContentReport):
    """
    Package (install|update|uninstall) report.
    Calculates the num_changes.
    """

    def set_succeeded(self, details):
        num_changes = \
            len(details['resolved']) + \
            len(details['deps'])
        super(PackageReport, self).set_succeeded(details, num_changes)


class GroupReport(ContentReport):
    """
    Package Group (install|update|uninstall) report.
    Calculates the num_changes.
    """

    def set_succeeded(self, details):
        num_changes = \
            len(details['resolved']) + \
            len(details['deps'])
        super(GroupReport, self).set_succeeded(details, num_changes)


class PackageHandler(ContentHandler):
    """
    The package (rpm) content handler.
    """

    @staticmethod
    def _impl(options):
        commit = options.get('apply', True)
        impl = Package(commit=commit)
        return impl

    def install(self, units, options):
        """
        Install packages.

        Args:
            units (collections.Iterable): Packages to be installed.
            options (dict): Handler specific options.

        Returns:
            PackageReport: A report.

        Notes:
            Unit is: {type_id:<str>, unit_key:<dict>}
        """
        report = PackageReport()
        package = self._impl(options)
        patterns = [Pattern(**u) for u in units]
        details = package.install(patterns)
        if details['failed']:
            report.set_failed(details)
        else:
            report.set_succeeded(details)
        return report

    def update(self, units, options):
        """
        Update packages.

        Args:
            units (collections.Iterable): Packages to be updated.
            options (dict): Handler specific options.

        Returns:
            PackageReport: A report.

        Notes:
            Unit is: {type_id:<str>, unit_key:<dict>}
        """
        report = PackageReport()
        _all = options.get('all', False)
        package = self._impl(options)

        if _all:
            patterns = []
        else:
            patterns = [Pattern(**u) for u in units]

        if patterns or _all:
            details = package.update(patterns)
            if details['failed']:
                report.set_failed(details)
            else:
                report.set_succeeded(details)
        return report

    def uninstall(self, units, options):
        """
        Uninstall packages.

        Args:
            units (collections.Iterable): Packages to be uninstalled.
            options (dict): Handler specific options.

        Returns:
            PackageReport: A report.

        Notes:
            Unit is: {type_id:<str>, unit_key:<dict>}
        """
        report = PackageReport()
        package = self._impl(options)
        patterns = [Pattern(**u) for u in units]
        details = package.uninstall(patterns)
        if details['failed']:
            report.set_failed(details)
        else:
            report.set_succeeded(details)
        return report


class GroupHandler(ContentHandler):
    """
    The package group content handler.
    """

    @staticmethod
    def _impl(options):
        commit = options.get('apply', True)
        impl = PackageGroup(commit=commit)
        return impl

    def install(self, units, options):
        """
        Install package group.

        Args:
            units (collections.Iterable): Groups to be installed.
            options (dict): Handler specific options.

        Returns:
            GroupReport: A report.

        Notes:
            Unit is: {type_id:<str>, unit_key:<dict>}
        """
        report = GroupReport()
        group = self._impl(options)
        names = [key['name'] for key in units]
        details = group.install(names)
        report.set_succeeded(details)
        return report

    def update(self, units, options):
        raise NotImplementedError()

    def uninstall(self, units, options):
        """
        Uninstall packages.

        Args:
            units (collections.Iterable): Groups to be uninstalled.
            options (dict): Handler specific options.

        Returns:
            GroupReport: A report.

        Notes:
            Unit is: {type_id:<str>, unit_key:<dict>}
        """
        report = GroupReport()
        group = self._impl(options)
        names = [key['name'] for key in units]
        details = group.uninstall(names)
        report.set_succeeded(details)
        return report


class ErratumHandler(ContentHandler):
    """
    The package (rpm) content handler.
    """

    @staticmethod
    def _impl(options):
        commit = options.get('apply', True)
        impl = Package(commit=commit)
        return impl

    def install(self, units, options):
        """
        Install Errata.

        Args:
            units (collections.Iterable): Errata to be installed.
            options (dict): Handler specific options.

        Returns:
            PackageReport: A report.

        Notes:
            Unit is: {type_id:<str>, unit_key:<dict>}
        """
        report = PackageReport()
        package = self._impl(options)
        advisories = [unit_key['id'] for unit_key in units]
        details = package.update(advisories=advisories)
        if details['failed']:
            report.set_failed(details)
        else:
            report.set_succeeded(details)
        return report

    def update(self, units, options):
        raise NotImplementedError()

    def uninstall(self, units, options):
        raise NotImplementedError()
