#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import mock

from cccp.protocols.rt.subscriber import (
    Subscription,
    Subscriber
)
from cccp.protocols.errors import SubscriptionError
from cccp.protocols.rt.lookup import IndicatorLuT

from twisted.trial import unittest


class SubscriptionTestCase(unittest.TestCase):
    def setUp(self):
        self.lut = IndicatorLuT()
        self.subscriber = Subscriber(self.lut)
        self.subject1 = mock.MagicMock()
        self.subject2 = mock.MagicMock()
        self.subscription = Subscription(
            self.subscriber,
            "id1234",
            "session1234",
            "session",
            "profile",
            [self.subject1, self.subject2]
        )

    def test_add_subjects(self):
        subject3 = mock.MagicMock()

        self.subscription.add_subjects([subject3])

        self.assertEquals(subject3.attach.called, True)
        self.assertEquals(subject3 in self.subscription.subjects, True)

    def test_del_subjects(self):
        subject3 = mock.MagicMock()

        self.subscription.add_subjects([subject3])
        self.subscription.del_subjects([subject3])

        self.assertEquals(subject3.detach.called, True)
        self.assertEquals(subject3 in self.subscription.subjects, False)


class SubscriberTestCase(unittest.TestCase):
    def setUp(self):
        self.lut = IndicatorLuT()
        self.subscriber = Subscriber(self.lut)

    @mock.patch("cccp.protocols.rt.subscriber.compute_key")
    def test_subscribe_session(self, mock_compute):
        mock_compute.return_value = "abcdkey"
        result = self.subscriber.subscribe(
            "username",
            "session",
            ["user_total_tasks_count"],
            "profile"
        )

        self.assertEquals(
            result,
            {
                'data': {
                    'user_total_tasks_count': {'value': 0}
                },
                'id': 'abcdkey'
            }
        )

    @mock.patch("cccp.protocols.rt.subscriber.compute_key")
    def test_subscribe_service(self, mock_compute):
        mock_compute.return_value = "abcdkey"

        result = self.subscriber.subscribe(
            "username",
            "service",
            ["users_count"]
        )

        self.assertEquals(
            result,
            {
                'data': {
                    'users_count': {'value': 0}
                },
                'id': 'abcdkey'
            }
        )

    def test_subscribe_invalid_type(self):
        self.assertRaises(
            SubscriptionError,
            self.subscriber.subscribe,
            'username',
            "invalid_type",
            ['users_count']
        )

    def test_subscribe_invalid_indicator(self):
        self.assertRaises(
            SubscriptionError,
            self.subscriber.subscribe,
            'username',
            "service",
            ["invalid_indic"]
        )

    def test_update_subscription_add_indicator_to_session(self):
        self.test_subscribe_session()

        result = self.subscriber.update_subscription(
            "abcdkey",
            ["user_managed_tasks_count"],
            [],
        )

        self.assertEquals(
            result,
            {
                'user_managed_tasks_count': {'value': 0}
            }
        )

    def test_update_subscription_add_invalid_indicator_to_session(self):
        self.test_subscribe_session()

        self.assertRaises(
            SubscriptionError,
            self.subscriber.update_subscription,
            "abcdkey",
            ["invalid_indic"],
            [],
        )

    def test_update_subscription_add_indicator_to_service(self):
        self.test_subscribe_service()

        result = self.subscriber.update_subscription(
            "abcdkey",
            ["available_users_count"],
            [],
        )

        self.assertEquals(
            result,
            {
                'available_users_count': {'value': 0}
            }
        )

    def test_update_subscription_add_invalid_indicator_to_service(self):
        self.test_subscribe_service()

        self.assertRaises(
            SubscriptionError,
            self.subscriber.update_subscription,
            "abcdkey",
            ["invalid_indic"],
            [],
        )

    def test_update_subscription_del_indicator_to_session(self):
        self.test_update_subscription_add_indicator_to_session()

        self.subscriber.update_subscription(
            "abcdkey",
            [],
            ['user_managed_tasks_count']
        )

        subscription = self.subscriber.subscriptions['abcdkey']

        indics_list = [subject.name for subject in subscription.subjects]

        self.assertEquals(indics_list, ['user_total_tasks_count'])

    def test_update_subscription_del_invalid_indicator_to_session(self):
        self.test_subscribe_session()

        self.assertRaises(
            SubscriptionError,
            self.subscriber.update_subscription,
            "abcdkey",
            [],
            ["invalid_indic"],
        )

    def test_update_subscription_del_indicator_to_service(self):
        self.test_update_subscription_add_indicator_to_service()

        self.subscriber.update_subscription(
            "abcdkey",
            [],
            ['available_users_count']
        )

        subscription = self.subscriber.subscriptions['abcdkey']

        indics_list = [subject.name for subject in subscription.subjects]

        self.assertEquals(indics_list, ['users_count'])

    def test_update_subscription_del_invalid_indicator_to_service(self):
        self.test_subscribe_service()

        self.assertRaises(
            SubscriptionError,
            self.subscriber.update_subscription,
            "abcdkey",
            [],
            ["invalid_indic"],
        )

    def test_update_subscription_with_unknown_subscription_id(self):

        self.assertRaises(
            SubscriptionError,
            self.subscriber.update_subscription,
            "unknownkey",
            [],
            ['available_users_count']
        )

    def test_get_subscription_values_session(self):
        self.test_update_subscription_add_indicator_to_session()

        result = self.subscriber.get_subscription_values(
            "abcdkey",
            ['user_total_tasks_count', 'user_managed_tasks_count'],
        )

        self.assertEquals(
            result,
            {
                'user_managed_tasks_count': {'value': 0},
                'user_total_tasks_count': {'value': 0}
            }
        )

    def test_get_subscription_values_service(self):
        self.test_update_subscription_add_indicator_to_service()

        result = self.subscriber.get_subscription_values(
            "abcdkey",
            ['users_count', 'available_users_count'],
        )

        self.assertEquals(
            result,
            {
                'available_users_count': {'value': 0},
                'users_count': {'value': 0}
            }
        )

    def test_unsubscribe(self):
        self.test_update_subscription_add_indicator_to_session()

        self.subscriber.unsubscribe("abcdkey")

        self.assertEquals("abcdkey" in self.subscriber.subscriptions, False)

    def test_unsubscribe_unknown_id(self):
        self.assertRaises(
            SubscriptionError,
            self.subscriber.unsubscribe,
            "unknownkey"
        )

    def test_unsubscribe_all(self):
        self.test_update_subscription_add_indicator_to_session()

        self.subscriber.unsubscribe_all()

        self.assertEquals("abcdkey" in self.subscriber.subscriptions, False)

    def test_prepareToSend(self):
        self.test_update_subscription_add_indicator_to_session()
        self.subscriber.send = mock.MagicMock()

        self.subscriber.prepareToSend(
            "abcdkey",
            "session",
            {"user_total_tasks_count": {'value': 0}}
        )

        self.subscriber.send.assert_called_once_with(
            "session",
            "username",
            {
                'user_total_tasks_count': {'value': 0}
            }
        )
