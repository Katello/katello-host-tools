import sys
import traceback as tb


class Report(object):
    """
    The base report.

    Attributes:
        succeeded (bool): Indicates whether or not a handler operation succeeded.
        details (dict): Operation result details.
        num_changes (int): The number of changes made during the operation.
        The granularity is up to the discretion of the handler.
    """

    def __init__(self):
        self.succeeded = True
        self.details = {}
        self.num_changes = 0

    def dict(self):
        """
        Dictionary representation of the report.

        Returns:
            dict: Self.
        """
        return self.__dict__

    def __str__(self):
        return str(self.dict())

    def __len__(self):
        return self.num_changes


class HandlerReport(Report):
    """
    The base handler report.

    Attributes:
        aggregation_key (str): The key used to aggregate details when
            updating another report.
    """

    @staticmethod
    def last_exception():
        """
        Get details of the last raised exception.

        Returns:
            dict: Details of last raised exception.
        """
        details = {}
        info = sys.exc_info()
        inst = info[1]
        trace = '\n'.join(tb.format_exception(*info))
        details['message'] = str(inst)
        details['trace'] = trace
        return details

    def __init__(self):
        Report.__init__(self)
        self.aggregation_key = None

    def set_succeeded(self, details=None, num_changes=0):
        """
        Called to indicate an operation succeeded.

        Args:
            details (dict): The details of the operation result.
            num_changes (int): The number of changes made during the operation.
                The granularity is up to the discretion of the handler.
        """
        self.succeeded = True
        self.details = (details or {})
        self.num_changes = num_changes

    def set_failed(self, details=None):
        """
        Called to indicate an operation failed.

        Args:
            details (dict): The details of the operation result.
        """
        self.succeeded = False
        self.details = (details or {})

    def update(self, report):
        """
        Update the specified report.

        Args:
            report (DispatchReport): A dispatch report.
        """
        self._update_succeeded(report)
        self._update_num_changes(report)
        self._update_details(report)

    def _update_succeeded(self, report):
        """
        Update the succeeded flag in the specified report.

        Args:
            report (DispatchReport): A dispatch report.
        """
        if not self.succeeded:
            report.succeeded = self.succeeded

    def _update_num_changes(self, report):
        """
        Update the num_changes in the specified report.

        Args:
            report (DispatchReport): A dispatch report.
        """
        if self.succeeded:
            report.num_changes += self.num_changes

    def _update_details(self, report):
        """
        Update the details in the specified report.
        The details are aggregated in the specified report using
        the aggregation key.

        Args:
            report (DispatchReport): A dispatch report.
        """
        report.details[self.aggregation_key] = dict(
            succeeded=self.succeeded,
            details=self.details)


class ContentReport(HandlerReport):
    """
    The content report is returned by handler methods
    implementing content unit operations.
    """
    pass


class DispatchReport(Report):
    """
    The (internal) dispatch report is returned for all handler methods
    dispatched to handlers.  It represents an aggregation of handler reports.
    The handler (class) reports are collated by type_id (content, distributor, system).
    The overall succeeded is True (succeeded) only if all of the handler reports have
    a succeeded of True (succeeded).
    Succeeded Example:
      { 'succeeded' : True,
        'num_changes' : 10,
        'reboot' : { 'scheduled' : False, details : {} },
        'details' : {
          'type_A' : { 'succeeded' : True, 'details' : {} },
          'type_B' : { 'succeeded' : True, 'details' : {} },
          'type_C' : { 'succeeded' : True, 'details' : {} },
        }
      }
    Failed Example:
      { 'succeeded' : False,
        'num_changes' : 6,
        'reboot' : { 'scheduled' : False, details : {} },
        'details' : {
          'type_A' : { 'succeeded' : True, 'details' : {} },
          'type_B' : { 'succeeded' : True, 'details' : {} },
          'type_C' : { 'succeeded' : False,
                       'details' : { 'message' : <message>, 'trace'=<trace> } },
        }
      }

    Attributes:
        succeeded (bool): The overall succeeded (succeeded|failed).
        details (dict): operation details keyed by aggregation_key.
            Each value is:
                { 'succeeded' : True, details : {} }
        num_changes (int): The number of changes made during the operation.
            The granularity is up to the discretion of the handlers.
    """

    def __init__(self):
        Report.__init__(self)
        self.reboot = dict(scheduled=False, details={})
