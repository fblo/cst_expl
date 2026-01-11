#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - SLAU <slau@interact-iv.com>


class CcxmlSubscriberError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class CcxmlRequesterError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class DispatchSubscriberError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class CcxmlConfError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class ConfigDBError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class SerializerError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class SerializerMethodError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class ConverterError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class DeserializerError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class UsageDBError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class ProcessViewerError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class ExplorerRequesterError(Exception):
    """
    .. todo::
        Add documentation
    """

    pass


class HeadRequesterError(Exception):
    """
    .. todo::
        Add documentation
    """

    def __init__(self, msg, result=0):
        super(HeadRequesterError, self).__init__(msg)
        self.result = result


class SubscriptionError(Exception):
    pass


class AvailabilityException(Exception):
    pass
