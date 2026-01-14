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

import getpass

from ivsync.utils import Client, handle_error
from ivsync.webadminobjects import WebAdminWhitelabel
from twisted.enterprise import adbapi
from twisted.python import log
from twisted.internet import defer


class WebAdminClient(Client):
    def _parse_credentials(self, args):
        self._portal_host = args.portal_host
        self._portal_username = args.portal_user
        self._portal_password = args.portal_password \
            or getpass.getpass("Portal DB password: ")
        self._portal_db_name = args.portal_db

        self._wa_host = args.webadmin_host
        self._wa_username = args.webadmin_user
        self._wa_password = args.webadmin_password \
            or getpass.getpass("WebAdmin DB password: ")
        self._wa_db_name = args.webadmin_db

    def _initialise_client(self):
        log.msg("Initialising DB clients.")
        self.portal_db = adbapi.ConnectionPool(
            "MySQLdb",
            cp_reconnect=True,
            host=self._portal_host,
            db=self._portal_db_name,
            user=self._portal_username,
            passwd=self._portal_password,
            charset='utf8', use_unicode=False)

        self.wa_db = adbapi.ConnectionPool(
            "MySQLdb",
            cp_reconnect=True,
            host=self._wa_host,
            db=self._wa_db_name,
            user=self._wa_username,
            passwd=self._wa_password,
            charset='utf8', use_unicode=False)

    def _test_client(self, client):
        return client.runQuery('select 1')

    def _test(self):
        log.msg("Testing DB connectivity.")
        deferreds = [
            self._test_client(self.portal_db),
            self._test_client(self.wa_db)
        ]

        d = defer.gatherResults(deferreds)
        d.chainDeferred(self.ready_deferred)

    def _test_success_msg(self):
        return "Connectivity test to DBs succeeded!"

    def get_whitelabels(self, wl_filter=None):
        query = ("select distinct(provider_id) as whitelabels "
                 "from adm_customers")
        args = None

        if wl_filter:
            query += " where provider_id = %s"
            args = (wl_filter,)

        query += " order by whitelabels"

        d = self.query_portal(query, args)

        def build_objects(result):
            return [WebAdminWhitelabel(value[0], self) for value in result]

        d.addCallbacks(build_objects, handle_error)

        return d

    def query_portal(self, query, args=None):
        if args:
            printable_query = query % args
        else:
            printable_query = query

        log.msg("Portal SQL:", printable_query)
        return self.portal_db.runQuery(query, args)

    def query_db(self, query, args=None):
        if args:
            printable_query = query % args
        else:
            printable_query = query

        log.msg("WebAdmin SQL:", printable_query)
        return self.wa_db.runQuery(query, args)