#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import mock

from cccp.protocols.converter import Converter
from cccp.protocols.commons import IncrementIdReservation
from cccp.protocols.dispatch import BaseDispatchClient
from cccp.protocols.errors import SubscriptionError
from twisted.trial import unittest


class BaseDispatchClientTestCase(unittest.TestCase):
    def setUp(self):
        self.base = BaseDispatchClient(reset_time=None)

    def test_init(self):
        self.assertIsInstance(self.base.converter, Converter)
        self.assertIsInstance(self.base._service_xqueries_list, list)
        self.assertIsInstance(self.base._user_xqueries_list, list)
        self.assertIsInstance(self.base._withdrawal_xqueries_list, list)
        self.assertIsInstance(self.base.next_format_id, IncrementIdReservation)
        self.assertIsInstance(self.base.next_idx, IncrementIdReservation)
        self.assertEquals(self.base.service_done, False)
        self.assertEquals(self.base.tables, {})

    def test_stop_view_with_idx(self):
        self.base.stop_query = mock.MagicMock()
        self.base.query_list = mock.MagicMock()
        self.base.next_idx = mock.MagicMock()
        self.base.next_format_id = mock.MagicMock()
        self.base.tables = {"idx": ("", "format_id", "", ["ids"])}
        self.base.stop_view("idx")

        self.base.stop_query.assert_called_with("idx")
        # self.base.next_idx.release.assert_called_with("idx")
        # self.base.next_format_id.releaseassert_called_once_with("format_id")
        self.assertEquals(self.base.query_list.called, False)

    def test_on_list_response_no_idx(self):
        self.base.stop_query = mock.MagicMock()
        self.base.on_list_response("session", "idx", "object")
        self.base.stop_query.assert_called_once_with("idx")

    def test_on_object_response_no_idx(self):
        self.base.stop_query = mock.MagicMock()
        self.base.on_object_response("session", "idx", "object", "obj_id")
        self.base.stop_query.assert_called_once_with("idx")

    def test_on_object_response_with_idx_service_list(self):
        self.base.stop_query = mock.MagicMock()
        self.base.subscriptions = mock.MagicMock()
        self.base.on_session_update = mock.MagicMock()
        self.base.on_service_list = mock.MagicMock()

        self.base.tables = {1: ({"obj_id": [1, 2]}, 0, ["1", "2"], 0)}
        self.base._session_format = ["format1"]
        object = mock.MagicMock()
        object.values = [object]
        object.value = "value"
        object.field_index = 0
        self.base.on_object_response("session", 1, object, "obj_id")

        self.base.on_service_list.assert_called_once_with([1, 2])

    def test_on_service_list(self):
        self.base.subscriptions = mock.MagicMock()
        self.base.view_change = mock.MagicMock()
        self.base.on_add_queues = mock.MagicMock()
        self.base.service_datas = {
            "name1": [
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
            ]
        }
        object = ['{"queue1": {"type": "queue", "queue": "name1"}}', "user"]

        self.base.on_service_list(object)
        self.base.on_add_queues.assert_called_once_with('user', {})

    def test_compute_defaults(self):
        format = ["count", "_date", "duration", "duration('0')", "count('0')"]
        result = self.base.compute_defaults(format)
        self.assertEquals(result, [None, 0, 0, 0, 0])

    def test_set_format(self):
        self.base.next_format_id = mock.MagicMock()
        self.base.next_format_id.reserve.return_value = 1234
        self.base.set_object_format = mock.MagicMock()
        self.base.converter = mock.MagicMock()
        cst_format = mock.MagicMock()
        xqueries_table = {}
        self.base.converter.create_cst_object.return_value = (
            cst_format,
            xqueries_table
        )

        result = self.base.set_format(["format"], 'db_root', "type")
        self.base.converter.create_cst_object.assert_called_once_with(
            ["format"]
        )
        self.base.set_object_format.assert_called_on_with(cst_format)
        self.assertEquals(self.base.next_format_id.reserve.called, True)
        self.assertEquals(result, 1234)

    @mock.patch("cccp.protocols.rt.subscriber.compute_key")
    def test_subscribe_session_one(self, mock_compute):
        mock_compute.return_value = "computed_key"
        result = self.base.subscribe(
            "session_name",
            "session",
            indicators = ["user_total_tasks_count"],
            profile_name = "profile_name"
        )

        self.assertEquals(
            result,
            {
                'data': {
                    'user_total_tasks_count': {'value': 0}
                },
                'id': 'computed_key'
            }
        )

    @mock.patch("cccp.protocols.rt.subscriber.compute_key")
    def test_subscribe_session_multi(self, mock_compute):
        mock_compute.return_value = "computed_key"
        result = self.base.subscribe(
            "session_name",
            "session",
            indicators = [
                "user_total_tasks_count", "user_managed_tasks_count"
            ],
            profile_name = "profile_name"
        )

        self.assertEquals(
            result,
            {
                'data': {
                    'user_managed_tasks_count': {'value': 0},
                    'user_total_tasks_count': {'value': 0}
                },
                'id': 'computed_key'
            }
        )

    @mock.patch("cccp.protocols.rt.subscriber.compute_key")
    def test_subscribe_service_one(self, mock_compute):
        mock_compute.return_value = "computed_key"
        result = self.base.subscribe(
            "service_a",
            "service",
            indicators = ["users_count"],
        )

        self.assertEquals(
            result,
            {
                'data': {
                    'users_count': {'value': 0}
                },
                'id': 'computed_key'
            }
        )

    @mock.patch("cccp.protocols.rt.subscriber.compute_key")
    def test_subscribe_service_multi(self, mock_compute):
        mock_compute.return_value = "computed_key"
        result = self.base.subscribe(
            "service_a",
            "service",
            indicators = ["users_count", "available_users_count"],
        )

        self.assertEquals(
            result,
            {
                'data': {
                    'users_count': {'value': 0},
                    'available_users_count': {'value': 0},
                },
                'id': 'computed_key'
            }
        )

    def test_subscribe_failure_invalid_type(self):
        self.assertRaises(
            SubscriptionError,
            self.base.subscribe,
            'service_a',
            "invalid_type",
            indicators = ['users_count']
        )

    def test_subscribe_failure_unknown_invalid(self):
        self.assertRaises(
            SubscriptionError,
            self.base.subscribe,
            'service_a',
            "service",
            indicators = ['invalid_indic']
        )

    def test_unsubscribe_remove(self):
        self.test_subscribe_service_one()

        self.base.unsubscribe("computed_key")

        self.assertEquals(
            'computed_key' in self.base.subscriber.subscriptions,
            False
        )

    def test_unsubscribe_update(self):
        self.test_subscribe_session_multi()

        indicators = [
            x.name for x in self.base.subscriber.subscriptions[
                'computed_key'].subjects
        ]
        self.assertEquals(
            indicators,
            [
                'user_total_tasks_count',
                'user_managed_tasks_count'
            ]
        )

        self.base.unsubscribe(
            "computed_key",
            ["user_total_tasks_count"]
        )

        indicators = [
            x.name for x in self.base.subscriber.subscriptions[
                'computed_key'].subjects
        ]

        self.assertEquals(
            indicators,
            ["user_managed_tasks_count"]
        )

    def test_unsubscribe_remove_failure_invalid_subscription_id(self):
        self.assertRaises(
            SubscriptionError,
            self.base.unsubscribe,
            "invalid_sub_id"
        )

    def test_unsubscribe_update_failure_invalid_indicator(self):
        self.test_subscribe_session_multi()

        self.assertRaises(
            SubscriptionError,
            self.base.unsubscribe,
            "computed_key",
            ["invalid_indic"]

        )

    def test_update_subscription(self):
        self.test_subscribe_session_one()

        values = self.base.update_subscription(
            "computed_key",
            "session",
            ["user_managed_tasks_count"]
        )

        self.assertEquals(
            values,
            {
                'user_managed_tasks_count': {'value': 0}
            }
        )

    def test_update_subscription_failure_unknown_indicator(self):
        self.test_subscribe_session_one()

        self.assertRaises(
            SubscriptionError,
            self.base.update_subscription,
            "computed_key",
            "session",
            ['invalid_indic']
        )
