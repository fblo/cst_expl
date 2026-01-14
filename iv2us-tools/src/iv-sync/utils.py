#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's IV2US Tools.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>
#    - SLAU <slau@interact-iv.com>
#    - GRIC <gric@interact-iv.com>

from __future__ import division, print_function

from twisted.internet import reactor, defer
from twisted.python import log
from twisted.python.failure import NoCurrentExceptionError

DEFAULT_LANGUAGE = 'fr-FR'
RETURN_CODE = 0


__default_languages = {
    'fr': 'fr-FR',
    'sp': 'es-ES',
    'en': 'en-UK',
    'pt': 'pt-PT',
    'it': 'it-IT',
    'es': 'es-ES'
}


def format_language(lang):
    """
    @author: Momo inside Ju's brain.
    """
    if lang and len(lang) == 5:
        return lang

    elif not lang or lang == '' or len(lang) != 2:
        return DEFAULT_LANGUAGE

    else:
        return __default_languages.get(lang.lower(), DEFAULT_LANGUAGE)


def handle_error(failure):
    RETURN_CODE = 3
    try:
        log.err()
    except NoCurrentExceptionError:
        log.msg(failure)

    reactor.stop()  # pylint: disable=E1101


class BusinessObject(object):
    def __init__(self, name, client):
        self.name = name
        self._client = client


class Client(object):
    def __init__(self, args):
        self.ready_deferred = defer.Deferred()
        self.ready_deferred.addCallbacks(self._log_test_success, handle_error)

        self._parse_credentials(args)
        self._initialise_client()
        self._test()

    def _parse_credentials(self, args):
        raise NotImplementedError()

    def _initialise_client(self):
        raise NotImplementedError()

    def _test(self):
        raise NotImplementedError()

    def _test_success_msg(self):
        raise NotImplementedError()

    def _log_test_success(self, _):
        log.msg(self._test_success_msg())
