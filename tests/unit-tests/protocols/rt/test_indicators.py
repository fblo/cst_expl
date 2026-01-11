#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import mock

from twisted.trial import unittest

from datetime import datetime

from cccp.protocols.localtime import date_to_iso
from cccp.protocols.rt.indicators import (
    BasicIndicator,
    AdvancedIndicator,
    # Session
    UserTotalTasksCount,
    UserManagedTasksCount,
    UserLostTasksCount,
    UserAverageContactDuration,
    UserTransferredTasks,
    UserAverageHoldDuration,
    UserAverageRingingDuration,
    UserVocalTotalWithdrawalDuration,
    UserProfileName,
    UserDisplayName,
    UserVocalTotalNamedWithdrawalDuration,
    UserVocalMode,
    UserCurrentTaskManagedDate,
    SessionLastLoginDate,
    SessionLastLogoutDate,
    UserVocalState,
    ActiveSessionsCount,
    RecordIndicator,
    RecordEnabled,
    # Service
    UsersCount,
    AvailableUsersCount,
    ManagingUsersCount,
    CurrentTasksCount,
    WaitingTasksCount,
    AverageWaitingDuration,
    NotManageableTasksCount,
    CanceledTasksCount,
    ManagedTasksRate,
    ServiceDisplayName,
    TotalTasksCount,
    ManagedTasksCount,
    MaxDurationWaitingTasks,
    VocalSessionId
)


class BasicIndicatorTestCase(unittest.TestCase):
    def setUp(self):
        self.indic = BasicIndicator("name")

    def test_get(self):
        self.assertEquals(self.indic.get(), 0)

    def test_set(self):
        self.indic.notify = mock.MagicMock()
        self.indic.set(1)

        self.assertEquals(self.indic.notify.called, True)
        self.assertEquals(self.indic.get(), 1)


class AdvancedIndicatorTestCase(unittest.TestCase):
    def setUp(self):
        self.indic = AdvancedIndicator("name")

    def test_add_subject(self):
        _indic = BasicIndicator("foo")
        _indic.attach = mock.MagicMock()
        self.indic.add_subject(_indic)

        _indic.attach.assert_called_once_with(self.indic)
        self.assertEquals(self.indic.subjects[0], _indic)

    def test_del_subject(self):
        _indic = BasicIndicator("foo")
        _indic.detach = mock.MagicMock()
        self.indic.add_subject(_indic)

        self.indic.del_subject(_indic)

        _indic.detach.assert_called_once_with(self.indic)
        self.assertEquals(len(self.indic.subjects), 0)

    def test_update(self):
        _indic = BasicIndicator("foo")

        self.indic.compute = mock.MagicMock()
        self.indic.notify = mock.MagicMock()

        self.indic.add_subject(_indic)

        _indic.set(1)

        self.assertEquals(self.indic.compute.called, True)


# Session indicators


class UserTotalTasksCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {"total_inbound.count('0')": BasicIndicator("foo")}

        self.indic = UserTotalTasksCount(self.indicators)

    def test_compute(self):
        # Equation : x = indic1
        self.indicators["total_inbound.count('0')"].set(1)
        self.assertEquals(self.indic.get(),
            {'user_total_tasks_count': {'value': 1}}
        )


class UserManagedTasksCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {"managed_inbound.count('0')": BasicIndicator("foo")}
        self.indic = UserManagedTasksCount(self.indicators)

    def test_compute(self):
        # Equation : x = indic1
        self.indicators["managed_inbound.count('0')"].set(1)
        self.assertEquals(self.indic.get(),
            {'user_managed_tasks_count': {'value': 1}}
        )


class UserLostTasksCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {"lost_inbound.count('0')": BasicIndicator("foo")}
        self.indic = UserLostTasksCount(self.indicators)

    def test_compute(self):
        # Equation :x = indic1
        self.indicators["lost_inbound.count('0')"].set(1)
        self.assertEquals(self.indic.get(),
            {'user_lost_tasks_count': {'value': 1}}
        )


class UserAverageContactDurationTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "managed_inbound.count('0')": BasicIndicator("foo"),
            "task_state_contact.duration('0')": BasicIndicator("bar"),
        }
        self.indic = UserAverageContactDuration(self.indicators)

    def test_compute(self):
        # Equation : x = indic2 / indic1
        self.indicators["managed_inbound.count('0')"].set(2)
        self.indicators["task_state_contact.duration('0')"].set(4)
        self.assertEquals(
            self.indic.get(),
            {
                'user_average_contact_duration': {
                    'details': {
                        'denominator': 2,
                        'numerator': 4
                    },
                    'value': 2.0
                }
            }
        )


class UserTransferredTasksTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "redirected_inbound.count('0')": BasicIndicator("foo"),
            "transferred_inbound.count('0')": BasicIndicator("bar"),
        }
        self.indic = UserTransferredTasks(self.indicators)

    def test_compute(self):
        # Equation : x = indic1 + indic2
        self.indicators["redirected_inbound.count('0')"].set(1)
        self.indicators["transferred_inbound.count('0')"].set(1)
        self.assertEquals(self.indic.get(),
            {'user_transferred_tasks': {'value': 2}}
        )


class UserAverageHoldDurationTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "managed_inbound.count('0')": BasicIndicator("foo"),
            "task_state_held.duration('0')": BasicIndicator("bar")
        }
        self.indic = UserAverageHoldDuration(self.indicators)

    def test_compute(self):
        # Equation : x = indic2 / indic1
        self.indicators["managed_inbound.count('0')"].set(2)
        self.indicators["task_state_held.duration('0')"].set(4)
        self.assertEquals(
            self.indic.get(),
            {
                'user_average_hold_duration': {
                    'details': {
                        'denominator': 2,
                        'numerator': 4
                    },
                    'value': 2.0
                }
            }
        )


class UserAverageRingingDurationTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "total_inbound.count('0')": BasicIndicator("foo"),
            "task_state_ringing.duration('0')": BasicIndicator("bar")
        }
        self.indic = UserAverageRingingDuration(self.indicators)

    def test_compute(self):
        # Equation : x = indic2 / indic1
        self.indicators["total_inbound.count('0')"].set(2)
        self.indicators["task_state_ringing.duration('0')"].set(4)
        self.assertEquals(
            self.indic.get(),
            {
                'user_average_ringing_duration': {
                    'details': {
                        'denominator': 2,
                        'numerator': 4
                    },
                    'value': 2.0
                }
            }
        )


class UserVocalTotalWithdrawalDurationTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "state_group_pause.duration('0')": BasicIndicator("foo"),
        }
        self.indic = UserVocalTotalWithdrawalDuration(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        self.indicators["state_group_pause.duration('0')"].set(9)
        self.assertEquals(
            self.indic.get(),
            {
                'user_vocal_total_withdrawal_duration': {
                    'value': 9
                }
            }
        )


class UserProfileNameTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'sessions.last.session.profile_name': BasicIndicator('foo')
        }
        self.indic = UserProfileName(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        self.indicators["sessions.last.session.profile_name"].set("hamfoobar")
        self.assertEquals(
            self.indic.get(),
            {'user_profile_name': {'value': 'hamfoobar'}}
        )


class UserDisplayNameTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'name': BasicIndicator('foo')
        }
        self.indic = UserDisplayName(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        self.indicators["name"].set("hamfoobar")
        self.assertEquals(
            self.indic.get(),
            {'user_display_name': {'value': 'hamfoobar'}}
        )


class UserVocalTotalNamedWithdrawalDurationTestCase(unittest.TestCase):
    def setUp(self):
        self.indic = UserVocalTotalNamedWithdrawalDuration(
            "xxxxxxxxxxxxxxxxxFooxxxxxxxxxxxxxx"
        )

    def test_compute(self):
        # Equation : x = indic
        self.indic.totalNamedWithdrawalDuration.set(9)
        self.assertEquals(
            self.indic.get(),
            {
                'user_vocal_total_named_Foo_withdrawal_duration': {
                    'value': 9
                }
            }
        )


class UserVocalModeTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'last_state_name': BasicIndicator('foo')
        }
        self.indic = UserVocalMode(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        self.indicators['last_state_name'].set('foo')
        self.assertEquals(
            self.indic.get(),
            {
                'user_vocal_mode': {
                    'value': 'foo'
                }
            }
        )


class SessionLastLoginDateTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'sessions.last.session.login_date': BasicIndicator('foo')
        }
        self.indic = SessionLastLoginDate(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        start = datetime.now()
        self.indicators['sessions.last.session.login_date'].set(start)

        self.assertEquals(
            self.indic.get(),
            {
                'vocal_session_last_login_date': {
                    'value': date_to_iso(start)
                }
            }
        )


class SessionLastLogoutDateTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'sessions.last.session.logout_date': BasicIndicator('foo')
        }
        self.indic = SessionLastLogoutDate(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        end = datetime.now()
        self.indicators['sessions.last.session.logout_date'].set(end)

        self.assertEquals(
            self.indic.get(),
            {
                'session_last_logout_date': {
                    'value': date_to_iso(end)
                }
            }
        )


class UserCurrentTaskManagedDateTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'tasks.last.task.management_effective_date': BasicIndicator('foo'),
            'tasks.last.task.end_date': BasicIndicator('bar')
        }
        self.indic = UserCurrentTaskManagedDate(self.indicators)

    def test_compute(self):
        # Equation : x = start if start > end else ""
        end = datetime.now()
        start = datetime.now()
        self.indicators['tasks.last.task.end_date'].set(end)
        self.indicators['tasks.last.task.management_effective_date'].set(start)

        self.assertEquals(
            self.indic.get(),
            {
                'vocal_user_current_task_managed_start_date': {
                    'value': date_to_iso(start)
                }
            }
        )

        end = datetime.now()
        self.indicators['tasks.last.task.end_date'].set(end)

        self.assertEquals(
            self.indic.get(),
            {
                'vocal_user_current_task_managed_start_date': {
                    'value': ''
                }
            }
        )


class UserVocalStateTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'last_task_name': BasicIndicator('foo'),
            'busy_count': BasicIndicator('bar'),
            'last_state_display_name': BasicIndicator('ham'),
            'outbound_state.value': BasicIndicator('spar'),
            'outbound_hold_flag.value': BasicIndicator('bur'),
        }

        self.indic = UserVocalState(self.indicators)

    def test_compute(self):
        # Equation : using translation table, see code
        self.indicators['last_task_name'].set('foo_available')
        self.indicators['last_state_display_name'].set("traitement d'appel")
        self.assertEquals(
            self.indic.get(),
            {
                'user_vocal_state': {
                    'value': 'available'
                }
            }
        )

        self.indicators['busy_count'].set(1)
        self.indicators['last_task_name'].set('processing')
        self.assertEquals(
            self.indic.get(),
            {
                'user_vocal_state': {
                    'value': 'trying'
                }
            }
        )


class ActiveSessionsCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'logged_count': BasicIndicator('foo')
        }

        self.indic = ActiveSessionsCount(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        self.indicators['logged_count'].set(44)

        self.assertEquals(
            self.indic.get(),
            {
                'active_sessions_count': {
                    'value': 44
                }
            }
        )


class RecordIndicatorTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'sessions.last.session.last_record.value': BasicIndicator('foo'),
            'sessions.last.session.session_id': BasicIndicator('bar')
        }
        self.indicators[
            'sessions.last.session.session_id'].value = "foobar_session"
        self.indicators['sessions.last.session.last_record.value'].value = None

        self.indic = RecordIndicator(self.indicators)

    def test_compute(self):
        # Equation : if init: x = indic else init = True
        self.indicators['sessions.last.session.last_record.value'].set(
            "{foo: 1}"
        )
        self.assertEquals(
            self.indic.get(),
            {'record_indicator': {'foo': 1}}
        )

        self.indicators['sessions.last.session.last_record.value'].set(
            "{foo: 2}"
        )
        self.assertEquals(
            self.indic.get(),
            {
                'record_indicator': {'foo': 2},
            }
        )


class RecordEnabledTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'sessions.last.session.record_active.value': BasicIndicator('foo')
        }
        self.indicators[
            'sessions.last.session.record_active.value'].value = None

        self.indic = RecordEnabled(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        self.indicators['sessions.last.session.record_active.value'].set(0)
        self.assertEquals(
            self.indic.get(),
            {
                'record_enabled': {'value': 0}
            }
        )


class VocalSessionIdTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "sessions.last.session.session_id": BasicIndicator('foo')
        }

        self.indic = VocalSessionId(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        self.indicators['sessions.last.session.session_id'].set('goobar')
        self.assertEquals(
            self.indic.get(),
            {
                'vocal_session_id': {'value': 'goobar'}
            }
        )


# Service indicators


class UsersCountTestCaseTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "latent_sessions_count": BasicIndicator("foo"),
            "logged_sessions_count": BasicIndicator("bar")
        }
        self.indic = UsersCount(self.indicators)

    def test_compute(self):
        # Equation : x = indic1 + indic2
        self.indicators["latent_sessions_count"].set(1)
        self.assertEquals(self.indic.get(), {'users_count': {'value': 1}})

        self.indicators["logged_sessions_count"].set(1)
        self.assertEquals(self.indic.get(), {'users_count': {'value': 2}})


class AvailableUsersCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "logged_sessions_count": BasicIndicator("foo"),
            "working_sessions_count": BasicIndicator("bar")
        }
        self.indic = AvailableUsersCount(self.indicators)

    def test_compute(self):
        # Equation : x = indic1 - indic2
        self.indicators["logged_sessions_count"].set(1)
        self.assertEquals(self.indic.get(),
            {'available_users_count': {'value': 1}}
        )

        self.indicators["working_sessions_count"].set(1)
        self.assertEquals(self.indic.get(),
            {'available_users_count': {'value': 0}}
        )


class ManagingUsersCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "working_sessions_count": BasicIndicator("foo")
        }
        self.indic = ManagingUsersCount(self.indicators)

    def test_compute(self):
        # Equation : x = indic1
        self.indicators["working_sessions_count"].set(1)
        self.assertEquals(self.indic.get(),
            {'managing_users_count': {'value': 1}}
        )


class CurrentTasksCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "running_tasks_count": BasicIndicator("foo")
        }
        self.indic = CurrentTasksCount(self.indicators)

    def test_compute(self):
        # Equation : x = indic1
        self.indicators["running_tasks_count"].set(1)
        self.assertEquals(self.indic.get(),
            {'current_tasks_count': {'value': 1}}
        )


class WaitingTasksCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indic = WaitingTasksCount("foo")

    def test_compute(self):
        # Equation : x = indic1
        self.indic.set(1)
        self.assertEquals(self.indic.get(),
            {'waiting_tasks_count': {'value': 1}}
        )


class AverageWaitingDurationTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "waiting_duration.count('0')": BasicIndicator("foo"),
            "managed_tasks.count('0')": BasicIndicator("bar"),
            "failed_tasks.count('0')": BasicIndicator("krf")
        }

        self.indic = AverageWaitingDuration(self.indicators)

    def test_compute(self):
        # Equation : x = indic1 / (indic2 + indic3)
        self.indicators["waiting_duration.count('0')"].set(4)

        self.assertEquals(
            self.indic.get(),
            {
                'average_waiting_duration': {
                    'details': {
                        'denominator': 0,
                        'numerator': 0
                    },
                    'value': 0
                }
            }
        )

        self.indicators["managed_tasks.count('0')"].set(1)
        self.indicators["failed_tasks.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {
                'average_waiting_duration': {
                    'details': {
                        'denominator': 2,
                        'numerator': 4
                    },
                    'value': 2.0
                }
            }
        )


class NotManageableTasksCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "max_waiting_time_threshold.count('0')": BasicIndicator("foo"),
            "max_estimated_waiting_time_"
            "threshold.count('0')": BasicIndicator("bar"),
            "not_manageable_with_latent_"
            "users.count('0')": BasicIndicator("krf"),
            "not_manageable_without_latent_"
            "users.count('0')": BasicIndicator("jrk"),
        }

        self.indic = NotManageableTasksCount(
            self.indicators
        )

    def test_compute(self):
        # Equation : x = indic1 + indic2 + indic3 + indic4
        self.indicators["max_waiting_time_threshold.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {'not_manageable_tasks_count': {'value': 1}}
        )

        self.indicators["max_estimated_waiting_time_"
            "threshold.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {'not_manageable_tasks_count': {'value': 2}}
        )

        self.indicators["not_manageable_with_latent_users.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {'not_manageable_tasks_count': {'value': 3}}
        )

        self.indicators["not_manageable_without_latent_"
            "users.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {'not_manageable_tasks_count': {'value': 4}}
        )


class CanceledTasksCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "failed_tasks.count('0')": BasicIndicator("foo"),
            "max_waiting_time_threshold.count('0')": BasicIndicator("bar"),
            "max_estimated_waiting_time_"
            "threshold.count('0')": BasicIndicator("krf"),
            "not_manageable_with_latent_"
            "users.count('0')": BasicIndicator("jrk"),
            "not_manageable_without_latent_"
            "users.count('0')": BasicIndicator("lol")
        }

        self.indic = CanceledTasksCount(
            self.indicators
        )

    def test_compute(self):
        # Equation : x = indic1 - (indic2 + indic3 + indic4 + indic5)
        self.indicators["failed_tasks.count('0')"].set(5)

        self.assertEquals(
            self.indic.get(),
            {'canceled_tasks_count': {'value': 5}}
        )

        self.indicators["max_waiting_time_threshold.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {'canceled_tasks_count': {'value': 4}}
        )

        self.indicators["max_estimated_waiting_time_"
            "threshold.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {'canceled_tasks_count': {'value': 3}}
        )

        self.indicators["not_manageable_with_latent_users.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {'canceled_tasks_count': {'value': 2}}
        )

        self.indicators["not_manageable_without_latent_"
            "users.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {'canceled_tasks_count': {'value': 1}}
        )


class ManagedTasksRateTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "managed_tasks.count('0')": BasicIndicator("foo"),
            "failed_tasks.count('0')": BasicIndicator("bar")
        }

        self.indic = ManagedTasksRate(
            self.indicators
        )

    def test_compute(self):
        # Equation : x = indic1 / (indic1 + indic2) * 100
        self.indicators["managed_tasks.count('0')"].set(2)
        self.indicators["failed_tasks.count('0')"].set(1)

        self.assertEquals(
            self.indic.get(),
            {
                'managed_tasks_rate': {
                    'details': {
                        'denominator': 3,
                        'numerator': 2
                    },
                    'value': 2.0 / 3.0 * 100
                }
            }
        )


class ServiceDisplayNameTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            'display_name': BasicIndicator('foo')
        }

        self.indic = ServiceDisplayName(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        self.indicators['display_name'].set('foobarham')
        self.assertEquals(
            self.indic.get(),
            {
                'service_display_name': {'value': 'foobarham'}
            }
        )


class TotalTasksCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "managed_tasks.count('0')": BasicIndicator('foo'),
            "failed_tasks.count('0')": BasicIndicator('ham')
        }

        self.indic = TotalTasksCount(self.indicators)

    def test_compute(self):
        # Equation : x = indic1 + indic2
        self.indicators["managed_tasks.count('0')"].set(4)
        self.indicators["failed_tasks.count('0')"].set(4)

        self.assertEquals(
            self.indic.get(),
            {
                'total_tasks_count': {'value': 8}
            }
        )


class ManagedTasksCountTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "managed_tasks.count('0')": BasicIndicator('foo')
        }

        self.indic = ManagedTasksCount(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        self.indicators["managed_tasks.count('0')"].set(7)
        self.assertEquals(
            self.indic.get(),
            {
                'managed_tasks_count': {'value': 7}
            }
        )


class MaxDurationWaitingTasksTestCase(unittest.TestCase):
    def setUp(self):
        self.indicators = {
            "waiting_duration.max('0')": BasicIndicator('foo')
        }

        self.indic = MaxDurationWaitingTasks(self.indicators)

    def test_compute(self):
        # Equation : x = indic
        date = datetime.now()
        self.indicators["waiting_duration.max('0')"].set(date)
        self.assertEquals(
            self.indic.get(),
            {
                'max_duration_waiting_tasks': {'value': date}
            }
        )
