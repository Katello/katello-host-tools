from gettext import gettext as _
from logging import getLogger

from katello.agent.pulp.handler import PackageHandler, GroupHandler, ErratumHandler
from katello.agent.pulp.report import DispatchReport, HandlerReport


log = getLogger(__name__)


# Handler Roles
SYSTEM = 0
CONTENT = 1


class HandlerNotFound(Exception):
    """
    Handler not found.
    """

    def __init__(self, **criteria):
        """
        @param criteria: The handler search criteria.
        @type criteria: dict
        """
        Exception.__init__(self, criteria)

    def __str__(self):
        return _('No handler for: {c}'.format(self.args[0]))


class Dispatcher(object):
    """
    The dispatch delegates operations to handlers based on
    the type_id specified in the request.
    """

    # Handler mapping.
    handler = {}

    @staticmethod
    def collated(units):
        """
        Content units collated by type_id.

        Args:
            units (collections.Iterable): A list of content units.

        Returns:
            dict: Units collated by type_id.
        """
        collated = {}
        for unit in units:
            type_id = unit['type_id']
            _list = collated.setdefault(type_id, [])
            _list.append(unit['unit_key'])
        return collated

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
        dispatch_report = DispatchReport()
        collated = self.collated(units)
        for type_id, units in collated.items():
            try:
                handler = self.find_handler(type_id, CONTENT)
                _report = handler.install(units, dict(options))
                _report.aggregation_key = type_id
                _report.update(dispatch_report)
            except Exception:
                log.exception(_('Handler failed.'))
                _report = HandlerReport()
                _report.aggregation_key = type_id
                _report.set_failed(HandlerReport.last_exception())
                _report.update(dispatch_report)
        return dispatch_report

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
        dispatch_report = DispatchReport()
        collated = self.collated(units)
        for type_id, units in collated.items():
            try:
                handler = self.find_handler(type_id, CONTENT)
                _report = handler.update(units, dict(options))
                _report.aggregation_key = type_id
                _report.update(dispatch_report)
            except Exception:
                log.exception(_('Handler failed.'))
                _report = HandlerReport()
                _report.aggregation_key = type_id
                _report.set_failed(HandlerReport.last_exception())
                _report.update(dispatch_report)
        return dispatch_report

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
        dispatch_report = DispatchReport()
        collated = self.collated(units)
        for type_id, units in collated.items():
            try:
                handler = self.find_handler(type_id, CONTENT)
                _report = handler.uninstall(units, dict(options))
                _report.aggregation_key = type_id
                _report.update(dispatch_report)
            except Exception:
                log.exception(_('Handler failed.'))
                _report = HandlerReport()
                _report.aggregation_key = type_id
                _report.set_failed(HandlerReport.last_exception())
                _report.update(dispatch_report)
        return dispatch_report

    def find_handler(self, type_id, role):
        """
        Find a handler by type ID and role.

        Args:
            type_id (int): A content type ID.
            role (int): The handler role requested.

        Returns:
            Handler: The requested handler.

        Raises:
            HandlerNotFound: When not found.
        """
        try:
            handler = self.handler[role][type_id]
        except KeyError:
            raise HandlerNotFound(type=type_id)
        else:
            return handler()


# Handler Registration.
Dispatcher.handler = {
    CONTENT: {
        'rpm': PackageHandler,
        'package_group': GroupHandler,
        'erratum': ErratumHandler,
    }
}
