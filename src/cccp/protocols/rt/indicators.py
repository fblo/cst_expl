#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from __future__ import division

import json

from cccp.protocols.localtime import date_to_iso

from ivcommons.patterns.observer import Subject, Observer
from ivcommons.log import Log

log = Log("protocols.rt.indicators")


class BasicIndicator(Subject, object):
    def __init__(self, name, subscribable=False):
        super(BasicIndicator, self).__init__()
        self.name = name
        self.rate = False
        self.value = None
        self.subscribable = subscribable
        self.is_advanced = False
        self._reset_value()

    def _reset_value(self):
        self.value = 0

    def reset(self):
        self._reset_value()
        self.notify()

    def set(self, value):
        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value
            self.notify()

    def get(self):
        return self.value


class AdvancedIndicator(Observer, BasicIndicator):
    def __init__(self, name, subscribable=True):
        super(AdvancedIndicator, self).__init__(name, subscribable)
        self.subjects = []
        self.is_advanced = True
        self._reset_value()

    def compute(self):
        pass

    def add_subject(self, indicator):
        self.subjects.append(indicator)
        indicator.attach(self)

    def del_subject(self, indicator):
        self.subjects.remove(indicator)
        indicator.detach(self)

    def update(self, subject):
        self.compute()

    def get(self):
        return {self.name: {'value': self.value}}


class AdvancedRateIndicator(AdvancedIndicator):
    def __init__(self, name, subscribable=True):
        super(AdvancedRateIndicator, self).__init__(name, subscribable)
        self._reset_value()

    def _reset_value(self):
        self.numerator = 0
        self.denominator = 0
        super(AdvancedRateIndicator, self)._reset_value()

    def get(self):
        values = super(AdvancedRateIndicator, self).get()
        values[self.name].update(
            {
                'details': {'numerator': self.numerator,
                            'denominator': self.denominator}
            }
        )
        return values


# Session's basic indicators

class TotalInboundCount(BasicIndicator):
    def __init__(self):
        super(TotalInboundCount, self).__init__(
            "total_inbound.count('0')",
        )


class ManagedInboundCount(BasicIndicator):
    def __init__(self):
        super(ManagedInboundCount, self).__init__(
            "managed_inbound.count('0')",
        )


class LostInboundCount(BasicIndicator):
    def __init__(self):
        super(LostInboundCount, self).__init__(
            "lost_inbound.count('0')",
        )


class TaskStateContactDuration(BasicIndicator):
    def __init__(self):
        super(TaskStateContactDuration, self).__init__(
            "task_state_contact.duration('0')"
        )


class UserContactDurationMaxBasic(BasicIndicator):
    def __init__(self):
        super(UserContactDurationMaxBasic, self).__init__(
            "contact_duration.max('0')"
        )


class RedirectedInboundCount(BasicIndicator):
    def __init__(self):
        super(RedirectedInboundCount, self).__init__(
            "redirected_inbound.count('0')"
        )


class TransferredInboundCount(BasicIndicator):
    def __init__(self):
        super(TransferredInboundCount, self).__init__(
            "transferred_inbound.count('0')"
        )

    def set(self, value):
        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value
        # Little variation of set() from BasicIndicator
        self.notify()


class TaskStateHeldDuration(BasicIndicator):
    def __init__(self):
        super(TaskStateHeldDuration, self).__init__(
            "task_state_held.duration('0')"
        )


class UserHoldDurationMaxBasic(BasicIndicator):
    def __init__(self):
        super(UserHoldDurationMaxBasic, self).__init__(
            "hold_duration.max('0')"
        )


class TaskStateRingingDuration(BasicIndicator):
    def __init__(self):
        super(TaskStateRingingDuration, self).__init__(
            "task_state_ringing.duration('0')"
        )


class UserRingingDurationMaxBasic(BasicIndicator):
    def __init__(self):
        super(UserRingingDurationMaxBasic, self).__init__(
            "ringing_duration.max('0')"
        )


class TotalWithdrawalDuration(BasicIndicator):
    def __init__(self):
        super(TotalWithdrawalDuration, self).__init__(
            "state_group_pause.duration('0')"
        )


class TotalOutboundDuration(BasicIndicator):
    def __init__(self):
        super(TotalOutboundDuration, self).__init__(
            "state_group_outbound.duration('0')"
        )


class ProfileName(BasicIndicator):
    def __init__(self):
        super(ProfileName, self).__init__("sessions.last.session.profile_name")


class DisplayName(BasicIndicator):
    def __init__(self):
        super(DisplayName, self).__init__("name")


class TotalNamedWithdrawalDuration(BasicIndicator):
    def __init__(self, name):
        super(TotalNamedWithdrawalDuration, self).__init__(name)


class Mode(BasicIndicator):
    def __init__(self):
        super(Mode, self).__init__('last_state_name')
        self._reset_value()

    def _reset_value(self):
        self.value = "disabled"

    def set(self, value):
        if value:
            # Hide the ugly names
            known_values = {
                'traitement': "inbound",
                'sortant': "outbound",
                'sortant2': "outbound",
                'supervision': "supervision",
                'disabled': "disabled"
            }

            if value[:5] == "pause":
                mode = "withdrawal"

            else:
                try:
                    mode = known_values[value]
                except KeyError:
                    mode = value
            super(Mode, self).set(mode)


class SessionId(BasicIndicator):
    def __init__(self):
        super(SessionId, self).__init__("sessions.last.session.session_id")


class LastLoginDate(BasicIndicator):
    def __init__(self):
        super(LastLoginDate, self).__init__('sessions.last.session.login_date')

    def _reset_value(self):
        pass


class LastLogoutDate(BasicIndicator):
    def __init__(self):
        super(LastLogoutDate, self).__init__(
            'sessions.last.session.logout_date'
        )


class TaskStartDate(BasicIndicator):
    def __init__(self):
        super(TaskStartDate, self).__init__('tasks.last.task.start_date')


class TaskManagedStartDate(BasicIndicator):
    def __init__(self):
        super(TaskManagedStartDate, self).__init__(
            'tasks.last.task.management_effective_date'
        )


class TaskManagedEndDate(BasicIndicator):
    def __init__(self):
        super(TaskManagedEndDate, self).__init__('tasks.last.task.end_date')


class VocalState(BasicIndicator):
    def __init__(self):
        super(VocalState, self).__init__('last_task_name')


class VocalStateDisplayName(BasicIndicator):
    def __init__(self):
        super(VocalStateDisplayName, self).__init__('last_state_display_name')


class VocalStateStartDate(BasicIndicator):
    def __init__(self):
        super(VocalStateStartDate, self).__init__('last_state_date')


class SessionLogged(BasicIndicator):
    def __init__(self):
        super(SessionLogged, self).__init__('sessions.last.session.logged')
        self.value = None

    def _reset_value(self):
        # No reset for this indicator, if we turn it at 0 or None,
        # it will delete the Session from its Profile!
        pass


class BusyCount(BasicIndicator):
    def __init__(self):
        super(BusyCount, self).__init__('busy_count')


class RecordActive(BasicIndicator):
    def __init__(self):
        super(RecordActive, self).__init__(
            'sessions.last.session.record_active.value'
        )

    def get(self):
        if self.value:
            flag = int(self.value)
            return {'current': bool(flag % 2), 'auto': flag > 1}

        else:
            return {'current': False, 'auto': False}


class LastRecord(BasicIndicator):
    def __init__(self):
        super(LastRecord, self).__init__(
            'sessions.last.session.last_record.value'
        )

    def _reset_value(self):
        self.value = None


class CurrentSpies(BasicIndicator):
    def __init__(self):
        super(CurrentSpies, self).__init__(
            'sessions.last.session.current_spies.value'
        )

    def _reset_value(self):
        self.value = None


class Interface(BasicIndicator):
    def __init__(self):
        super(Interface, self).__init__('sessions.last.session.current_mode')


class PhoneURI(BasicIndicator):
    def __init__(self):
        super(PhoneURI, self).__init__('sessions.last.session.phone_uri')


class StateStartDate(BasicIndicator):
    def __init__(self):
        super(StateStartDate, self).__init__(
            'states.last.state.start_date'
        )


class Login(BasicIndicator):
    def __init__(self):
        super(Login, self).__init__('login')


class TotalLegCount(BasicIndicator):
    def __init__(self):
        super(TotalLegCount, self).__init__('total_leg_count.value')

    def set(self, value):
        if type(value) == str:
            if value == "":
                value = 0
            else:
                value = int(value)

        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value

        self.notify()


class ContactedLegCount(BasicIndicator):
    def __init__(self):
        super(ContactedLegCount, self).__init__('contacted_leg_count.value')

    def set(self, value):
        if type(value) == str:
            if value == "":
                value = 0
            else:
                value = int(value)

        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value

        self.notify()


class FailedLegCount(BasicIndicator):
    def __init__(self):
        super(FailedLegCount, self).__init__('failed_leg_count.value')

    def set(self, value):
        if type(value) == str:
            if value == "":
                value = 0
            else:
                value = int(value)

        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value

        self.notify()


class CanceledLegCount(BasicIndicator):
    def __init__(self):
        super(CanceledLegCount, self).__init__('canceled_leg_count.value')

    def set(self, value):
        if type(value) == str:
            if value == "":
                value = 0
            else:
                value = int(value)

        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value

        self.notify()


class OutboundContactDuration(BasicIndicator):
    def __init__(self):
        super(OutboundContactDuration, self).__init__(
            'outbound_contact_duration.value')

    def set(self, value):
        if type(value) == str and value == "":
            value = 0

        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value

        self.notify()


class OutboundMaxContactDuration(BasicIndicator):
    def __init__(self):
        super(OutboundMaxContactDuration, self).__init__(
            'outbound_max_contact_duration.value')

    def set(self, value):
        if type(value) == str and value == "":
            value = 0

        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value

        self.notify()


class OutboundState(BasicIndicator):
    def __init__(self):
        super(OutboundState, self).__init__(
            'outbound_state.value'
        )


class OutboundHoldState(BasicIndicator):
    def __init__(self):
        super(OutboundHoldState, self).__init__(
            'outbound_hold_flag.value'
        )

    def set(self, value):
        if value is None:
            self.reset()
            return

        if value in (0, '0', 'false', 'False'):
            self.value = False

        else:
            self.value = True

        self.notify()


class LastOutboundCallStart(BasicIndicator):
    def __init__(self):
        super(LastOutboundCallStart, self).__init__(
            'last_outbound_call_start.value'
        )


class LastOutgoingActivity(BasicIndicator):
    def __init__(self):
        super(LastOutgoingActivity, self).__init__(
            'last_outgoing_activity.value'
        )


class LastTransferActivity(BasicIndicator):
    def __init__(self):
        super(LastTransferActivity, self).__init__(
            'last_transfer_activity.value'
        )

# Session' advanced indicators


class UserTotalTasksCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserTotalTasksCount, self).__init__("user_total_tasks_count")
        self.totalInboundCount = indicators["total_inbound.count('0')"]
        self.add_subject(self.totalInboundCount)

    def compute(self):
        self.set(self.totalInboundCount.get())

    def get(self):
        return super(UserTotalTasksCount, self).get()


class UserManagedTasksCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserManagedTasksCount, self).__init__("user_managed_tasks_count")
        self.managedInboundCount = indicators["managed_inbound.count('0')"]
        self.add_subject(self.managedInboundCount)

    def compute(self):
        return self.set(self.managedInboundCount.get())

    def get(self):
        return super(UserManagedTasksCount, self).get()


class UserLostTasksCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserLostTasksCount, self).__init__("user_lost_tasks_count")
        self.lostInboundCount = indicators["lost_inbound.count('0')"]
        self.add_subject(self.lostInboundCount)

    def compute(self):
        self.set(self.lostInboundCount.get())


class UserAverageContactDuration(AdvancedRateIndicator):
    def __init__(self, indicators):
        super(UserAverageContactDuration, self).__init__("user_average_contact_duration")
        self.managedInboundCount = indicators["managed_inbound.count('0')"]
        self.taskStateContactDuration = indicators["task_state_contact.duration('0')"]
        self.outboundContactDuraction = indicators["outbound_contact_duration.value"]
        self.add_subject(self.managedInboundCount)
        self.add_subject(self.taskStateContactDuration)
        self.add_subject(self.outboundContactDuraction)

    def compute(self):
        self.denominator = self.managedInboundCount.get()
        if self.denominator > 0:
            # On enleve le sortant car dans l'indicateur, entrant et sortant sont ensemble.
            # outbound = float(self.outboundContactDuraction.get() if self.outboundContactDuraction.get() else 0.0)
            outbound = 0.0
            self.numerator = float(self.taskStateContactDuration.get()) - outbound
            if self.numerator < 0.0:
                self.numerator = 0.0
            self.set(self.numerator / self.denominator)


class UserMaxContactDuration(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserMaxContactDuration, self).__init__(
            "user_max_duration_contact_tasks"
        )
        self.userContactDurationMaxBasic = indicators["contact_duration.max('0')"]
        self.outboundContactDuractionMaxBasic = indicators['outbound_max_contact_duration.value']
        self.add_subject(self.userContactDurationMaxBasic)
        self.add_subject(self.outboundContactDuractionMaxBasic)

    def compute(self):
        # On enleve le sortant car dans l'indicateur, entrant et sortant sont ensemble.
        # outbound = float(float(self.outboundContactDuractionMaxBasic.get()) if self.outboundContactDuractionMaxBasic.get() else 0.0)
        outbound = 0.0
        inbound = float(float(self.userContactDurationMaxBasic.get()) if self.userContactDurationMaxBasic.get() else 0.0)
        total = inbound - outbound
        if total < 0.0:
            total = 0.0
        self.set(str(total))


class UserTransferredTasks(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserTransferredTasks, self).__init__("user_transferred_tasks")
        self.redirectedInboundCount = indicators["redirected_inbound.count('0')"]
        self.transferredInboundCount = indicators["transferred_inbound.count('0')"]
        self.add_subject(self.redirectedInboundCount)
        self.add_subject(self.transferredInboundCount)

    def compute(self):
        self.set(
            self.redirectedInboundCount.get() +
            self.transferredInboundCount.get()
        )

    def set(self, value):
        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value
        # Little variation of set() from BasicIndicator
        self.notify()

    def get(self):
        return super(UserTransferredTasks, self).get()


class UserAverageHoldDuration(AdvancedRateIndicator):
    def __init__(self, indicators):
        super(UserAverageHoldDuration, self).__init__(
            "user_average_hold_duration"
        )
        self.managedInboundCount = indicators["managed_inbound.count('0')"]
        self.taskStateHeldDuration = \
            indicators["task_state_held.duration('0')"]
        self.add_subject(self.managedInboundCount)
        self.add_subject(self.taskStateHeldDuration)

    def compute(self):
        self.denominator = self.managedInboundCount.get()
        if self.denominator > 0:
            self.numerator = self.taskStateHeldDuration.get()
            self.set(self.numerator / self.denominator)


class UserMaxHoldDuration(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserMaxHoldDuration, self).__init__(
            "user_max_duration_hold_tasks"
        )
        self.userHoldDurationMaxBasic = indicators["hold_duration.max('0')"]
        self.add_subject(self.userHoldDurationMaxBasic)

    def compute(self):
        self.set(self.userHoldDurationMaxBasic.get())


class UserAverageRingingDuration(AdvancedRateIndicator):
    def __init__(self, indicators):
        super(UserAverageRingingDuration, self).__init__(
            "user_average_ringing_duration",
        )
        self.totalInboundCount = indicators["total_inbound.count('0')"]
        self.taskStateRingingDuration = \
            indicators["task_state_ringing.duration('0')"]
        self.add_subject(self.totalInboundCount)
        self.add_subject(self.taskStateRingingDuration)

    def compute(self):
        self.denominator = self.totalInboundCount.get()
        if self.denominator > 0:
            self.numerator = self.taskStateRingingDuration.get()
            self.set(self.numerator / self.denominator)


class UserMaxRingingDuration(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserMaxRingingDuration, self).__init__(
            "user_max_duration_ringing_tasks"
        )
        self.userRingingDurationMaxBasic = indicators[
            "ringing_duration.max('0')"]
        self.add_subject(self.userRingingDurationMaxBasic)

    def compute(self):
        self.set(self.userRingingDurationMaxBasic.get())


class UserVocalTotalWithdrawalDuration(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserVocalTotalWithdrawalDuration, self).__init__(
            "user_vocal_total_withdrawal_duration"
        )
        self.totalWithdrawalDuration = indicators[
            "state_group_pause.duration('0')"]
        self.add_subject(self.totalWithdrawalDuration)

    def compute(self):
        self.set(self.totalWithdrawalDuration.get())


class UserVocalTotalOutboundDuration(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserVocalTotalOutboundDuration, self).__init__(
            "user_vocal_total_outbound_duration"
        )
        self.totalOutboundDuration = indicators[
            "state_group_outbound.duration('0')"]
        self.add_subject(self.totalOutboundDuration)

    def compute(self):
        self.set(self.totalOutboundDuration.get())


class UserProfileName(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserProfileName, self).__init__("user_profile_name")
        self.profileName = indicators['sessions.last.session.profile_name']
        self.add_subject(self.profileName)

    def compute(self):
        self.set(self.profileName.get())


class UserDisplayName(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserDisplayName, self).__init__("user_display_name")
        self.displayName = indicators['name']
        self.add_subject(self.displayName)

    def compute(self):
        self.set(self.displayName.get())


class UserVocalTotalNamedWithdrawalDuration(AdvancedIndicator):
    def __init__(self, indicator):
        pause_name = indicator[17:-14]
        super(UserVocalTotalNamedWithdrawalDuration, self).__init__(
            "user_vocal_total_named_%s_withdrawal_duration" % (pause_name,)
        )

        self.totalNamedWithdrawalDuration = TotalNamedWithdrawalDuration(
            indicator
        )
        self.add_subject(self.totalNamedWithdrawalDuration)

    def compute(self):
        self.set(self.totalNamedWithdrawalDuration.get())


class UserVocalMode(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserVocalMode, self).__init__('user_vocal_mode')
        self.mode = indicators['last_state_name']
        self.add_subject(self.mode)

    def compute(self):
        self.set(self.mode.get())


class UserLogin(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserLogin, self).__init__('user_login')
        self.login = indicators['login']
        self.add_subject(self.login)

    def compute(self):
        self.set(self.login.get())


class SessionLastLoginDate(AdvancedIndicator):
    def __init__(self, indicators):
        super(SessionLastLoginDate, self).__init__(
            'vocal_session_last_login_date'
        )
        self.lastLoginDate = indicators['sessions.last.session.login_date']
        self.add_subject(self.lastLoginDate)

    def _reset_value(self):
        pass

    def compute(self):
        value = self.lastLoginDate.get()
        if value:
            value = date_to_iso(value)
        else:
            value = 0

        self.set(str(value))


class SessionLastLogoutDate(AdvancedIndicator):
    def __init__(self, indicators):
        super(SessionLastLogoutDate, self).__init__('session_last_logout_date')
        self.lastLogoutDate = indicators['sessions.last.session.logout_date']
        self.add_subject(self.lastLogoutDate)

    def compute(self):
        value = self.lastLogoutDate.get()
        if value:
            value = date_to_iso(value)
        else:
            value = 0

        self.set(str(value))


class UserCurrentTaskManagedDate(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserCurrentTaskManagedDate, self).__init__(
            'vocal_user_current_task_managed_start_date'
        )
        self.taskManagedStartDate = indicators[
            'tasks.last.task.management_effective_date']
        self.taskManagedEndDate = indicators['tasks.last.task.end_date']
        self.add_subject(self.taskManagedStartDate)
        self.add_subject(self.taskManagedEndDate)

    def _reset_value(self):
        self.value = None

    def compute(self):
        start = self.taskManagedStartDate.get()
        end = self.taskManagedEndDate.get()
        if start:
            try:
                if start > end:
                    self.set(str(date_to_iso(start)))
                else:
                    self.set("")

            except TypeError:
                self.set("")


class UserCurrentTaskStartDate(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserCurrentTaskStartDate, self).__init__(
            'vocal_user_current_task_start_date'
        )
        self.taskStartDate = indicators['tasks.last.task.start_date']
        self.taskManagedEndDate = indicators['tasks.last.task.end_date']
        self.lastOutboundCallStart = indicators[
            'last_outbound_call_start.value']
        self.add_subject(self.taskStartDate)
        self.add_subject(self.taskManagedEndDate)
        self.add_subject(self.lastOutboundCallStart)

    def _reset_value(self):
        self.value = None

    def compute(self):
        start = self.taskStartDate.get()
        end = self.taskManagedEndDate.get()
        outbound_start_time = self.lastOutboundCallStart.get()
        if outbound_start_time in ('stop', '0', 0, ""):
            if start:
                try:
                    if not end or start > end:
                        self.set(str(date_to_iso(start)))
                    else:
                        self.set("")

                except TypeError:
                    self.set("")

            elif outbound_start_time == 'stop':
                self.set("")
        else:
            # Send isoformat date like : 2017-03-29T15:28:39+0200
            self.set(outbound_start_time)


class UserVocalStateStartDate(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserVocalStateStartDate, self).__init__(
            'user_last_vocal_state_date'
        )
        self.stateStartDate = indicators['last_state_date']
        self.add_subject(self.stateStartDate)

    def _reset_value(self):
        pass

    def compute(self):
        value = self.stateStartDate.get()
        if value:
            value = date_to_iso(value)
        else:
            value = 0

        self.set(str(value))


class UserRawVocalState(AdvancedIndicator):
    def __init__(self, indicators, name="user_raw_vocal_state"):
        super(UserRawVocalState, self).__init__(name)
        self.vocalStateDisplayName = indicators["last_state_display_name"]
        self.add_subject(self.vocalStateDisplayName)

    def compute(self):
        self.set(self.vocalStateDisplayName.get())


class UserVocalState(UserRawVocalState):
    def __init__(self, indicators):
        super(UserVocalState, self).__init__(
            indicators, name='user_vocal_state'
        )
        self.vocalState = indicators['last_task_name']
        self.busyCount = indicators['busy_count']
        self.outboundState = indicators['outbound_state.value']
        self.outboundHold = indicators['outbound_hold_flag.value']
        self.add_subject(self.vocalState)
        self.add_subject(self.busyCount)
        self.add_subject(self.outboundState)
        self.add_subject(self.outboundHold)
        self.translation_table = {
            'assigning': 'invite',
            'processing': 'trying',
            'ringing': 'ringing',
            'managing': 'contact',
            'contact': 'contact',
            'held': 'hold',
            'post_managing': 'postprocessing',
            'temporization': 'postprocessing',
        }

    def compute(self):
        display_name = self.vocalStateDisplayName.get()
        if display_name == "appels sortants":
            outbound_state = self.outboundState.get()
            outbound_hold = self.outboundHold.get()

            if outbound_state in (0, 'disconnected'):
                value = 'outbound'

            elif outbound_hold:
                value = "outbound_hold"

            else:
                value = outbound_state

        else:
            if str(self.busyCount.get()) == "1":
                try:
                    value = self.translation_table[self.vocalState.get()]
                except KeyError:
                    value = self.vocalState.get()

            else:
                display_name = self.vocalStateDisplayName.get()
                if display_name != "traitement d'appel":
                    value = display_name
                else:
                    value = 'available'

        self.set(value)


class IsLogged(AdvancedIndicator):
    def __init__(self, indicators):
        super(IsLogged, self).__init__(
            'is_logged'
        )
        self.value = None
        self.sessionLogged = indicators['sessions.last.session.logged']
        self.add_subject(self.sessionLogged)

    def _reset_value(self):
        # No reset for this indicator, if we turn it at 0 or None,
        # it will delete the Session from its Profile!
        pass

    def reset(self):
        self._reset_value()

    def compute(self):
        self.set(self.sessionLogged.get())


class RecordIndicator(AdvancedIndicator):
    def __init__(self, indicators):
        super(RecordIndicator, self).__init__('record_indicator')
        self.lastRecord = indicators['sessions.last.session.last_record.value']
        self.add_subject(self.lastRecord)

    def _reset_value(self):
        self.value = None

    def reset(self):
        self._reset_value()

    def compute(self):
        value = self.lastRecord.get()
        if value and value[0] == '{':
            record_value = json.loads(value)
            self.set({self.name: record_value})

    def get(self):
        return self.value


class AutoRecordSessionWatcher(AdvancedIndicator):
    def __init__(self, indicators):
        super(AutoRecordSessionWatcher, self).__init__(
            'autorecord_session_watcher'
        )
        self.sessionId = indicators['sessions.last.session.session_id']
        self.login = indicators['login']
        self.sessionLogged = indicators['sessions.last.session.logged']
        self.add_subject(self.sessionId)
        self.add_subject(self.login)
        self.add_subject(self.sessionLogged)

    def _reset_value(self):
        self.value = {'login': None, 'session_id': None, 'logged': False}

    def compute(self):
        if self.login.get() and self.sessionId.get():
            value = {
                'login': self.login.get(),
                'session_id': self.sessionId.get(),
                'logged': self.sessionLogged.get(),
            }
            self.set({self.name: value})

    def get(self):
        return self.value


class CallRecordIndicator(AdvancedIndicator):
    def __init__(self, indicators):
        super(CallRecordIndicator, self).__init__('record_indicator')
        self.lastRecord = indicators['sessions.last.session.last_record.value']
        self.add_subject(self.lastRecord)

    def _reset_value(self):
        self.value = None

    def reset(self):
        self._reset_value()

    def compute(self):
        value = self.lastRecord.get()
        if value and value[0] == '{':
            record_value = json.loads(value)
            self.set(record_value)

    def get(self):
        return {'record_indicator': self.value}


class RecordEnabled(AdvancedIndicator):
    def __init__(self, indicators):
        super(RecordEnabled, self).__init__('record_enabled')
        self.recordActive = indicators[
            'sessions.last.session.record_active.value']
        self.add_subject(self.recordActive)

    def _reset_value(self):
        self.value = None

    def compute(self):
        self.set(self.recordActive.get())


class SessionCurrentSpies(AdvancedIndicator):
    def __init__(self, indicators):
        super(SessionCurrentSpies, self).__init__('current_spies')
        self.currentSpies = indicators[
            'sessions.last.session.current_spies.value'
        ]
        self.add_subject(self.currentSpies)

    def _reset_value(self):
        self.value = None

    def compute(self):
        data = self.currentSpies.get()
        result = []
        if data:
            _data = json.loads(data)
            for _login in _data:
                result.append(_login.split('AGENT')[1])

        self.set(list(set(result)))


class VocalSessionId(AdvancedIndicator):
    def __init__(self, indicators):
        super(VocalSessionId, self).__init__("vocal_session_id")
        self.sessionId = indicators['sessions.last.session.session_id']
        self.add_subject(self.sessionId)

    def compute(self):
        self.set(self.sessionId.get())


class VocalInterface(AdvancedIndicator):
    modes = {
        'Scheduling agent': 'scheduled',
        'phone login': 'phone',
        'unplug': 'unplug',
    }

    def __init__(self, indicators):
        super(VocalInterface, self).__init__('vocal_interface')
        self.interface = indicators['sessions.last.session.current_mode']
        self.add_subject(self.interface)

    def compute(self):
        self.set(self.modes.get(self.interface.get(), "interface"))


class UserVocalPosition(AdvancedIndicator):
    def __init__(self, indicators):
        super(UserVocalPosition, self).__init__('user_vocal_position')
        self.phoneURI = indicators["sessions.last.session.phone_uri"]
        self.add_subject(self.phoneURI)

    def compute(self):
        self.set(self.phoneURI.get())


class StateStartTime(AdvancedIndicator):
    def __init__(self, indicators):
        super(StateStartTime, self).__init__(
            "vocal_state_start_time"
        )

        self.start = indicators["states.last.state.start_date"]

        self.add_subject(self.start)

    def _reset_value(self):
        pass

    def compute(self):
        value = self.start.get()
        if value:
            value = date_to_iso(value)

        else:
            value = 0

        self.set(str(value))

# Session dailies indicators


class DailySumIndicator(AdvancedIndicator):
    def __init__(self, indicators, indicator_lut):
        super(DailySumIndicator, self).__init__(self._subscribable_name)
        self.indicator_lut = indicator_lut
        self.login = indicators['login']
        self.profile_name = indicators['sessions.last.session.profile_name']
        self.current_indicator = indicators[self._watched_indicator]
        self.add_subject(self.current_indicator)

    def compute(self):
        values = self.indicator_lut.get_daily_listener().get_indicator_value(
            self.profile_name.get(), self.login.get(),
            self._watched_indicator
        )
        value = int(float(self.current_indicator.get()))
        for val in values.values():
            if not val:
                continue
            value += int(float(val))
        self.set(value)

    def set(self, value):
        if value is None:
            self.reset()
            return

        if value != self.value:
            self.value = value

        self.notify()


class DailyMaxIndicator(DailySumIndicator):
    def compute(self):
        values = self.indicator_lut.get_daily_listener().get_indicator_value(
            self.profile_name.get(), self.login.get(),
            self._watched_indicator
        )
        value = int(float(self.current_indicator.get()))
        for val in values.values():
            if not val:
                continue
            if value < int(float(val)):
                value = int(float(val))
        self.set(value)


class UserTotalLegCount(DailySumIndicator):
    _watched_indicator = 'total_leg_count.value'
    _subscribable_name = 'user_total_leg_count'


class UserContactedLegCount(DailySumIndicator):
    _watched_indicator = 'contacted_leg_count.value'
    _subscribable_name = 'user_contacted_leg_count'


class UserFailedLegCount(DailySumIndicator):
    _watched_indicator = 'failed_leg_count.value'
    _subscribable_name = 'user_failed_leg_count'


class UserCanceledLegCount(DailySumIndicator):
    _watched_indicator = 'canceled_leg_count.value'
    _subscribable_name = 'user_canceled_leg_count'


class UserOutboundContactTotalDuration(DailySumIndicator):
    _watched_indicator = 'outbound_contact_duration.value'
    _subscribable_name = 'user_outbound_contact_total_duration'


class UserOutboundContactMaxDuration(DailyMaxIndicator):
    _watched_indicator = 'outbound_max_contact_duration.value'
    _subscribable_name = 'user_outbound_contact_maximum_duration'


class UserOutboundContactAverageDuration(DailySumIndicator):
    _watched_indicator = 'outbound_contact_duration.value'
    _subscribable_name = 'user_outbound_contact_average_duration'

    def __init__(self, indicators, indicator_lut):
        super(DailySumIndicator, self).__init__(self._subscribable_name)
        self.indicator_lut = indicator_lut
        self.login = indicators['login']
        self.profile_name = indicators['sessions.last.session.profile_name']
        self.current_indicator = indicators[self._watched_indicator]
        self.current_contact_count = indicators['contacted_leg_count.value']
        self.add_subject(self.current_indicator)

    def compute(self):
        contact_duration_values = \
            self.indicator_lut.get_daily_listener().get_indicator_value(
                self.profile_name.get(), self.login.get(),
                self._watched_indicator
            )
        contact_count_values = \
            self.indicator_lut.get_daily_listener().get_indicator_value(
                self.profile_name.get(), self.login.get(),
                'contacted_leg_count.value'
            )

        contact_duration_value = float(self.current_indicator.get())
        contact_count_value = int(self.current_contact_count.get())
        for val in contact_duration_values.values():
            if not val:
                continue
            contact_duration_value += float(val)

        for val in contact_count_values.values():
            if not val:
                continue
            contact_count_value += int(val)
        if not contact_count_value:
            # Avoid division by zero
            contact_count_value = 1

        value = int(contact_duration_value / contact_count_value)
        self.set(value)


class UserActivity(AdvancedIndicator):
    canceled_causes = ('Canceled', 'Temporarily Unavailable')
    failed_causes = ('Address Incomplete', 'No response', 'Busy Here')

    def __init__(self, indicators, indicator_lut):
        super(UserActivity, self).__init__("user_activity")
        self.indicator_lut = indicator_lut
        self.login = indicators['login']
        self.profile_name = indicators['sessions.last.session.profile_name']
        self.outgoing_activity = indicators['last_outgoing_activity.value']
        self.transfer_activity = indicators['last_transfer_activity.value']
        self.session_id = indicators['sessions.last.session.session_id']

        self.add_subject(self.outgoing_activity)
        self.add_subject(self.transfer_activity)

    def _reset_value(self):
        self.value = []

    def _get_state(self, values):
        if values.get('context') == 'file':
            return 'inbound'

        elif values.get('context') == 'sortant':
            return 'outbound'

        else:
            return values.get('context')

    def _get_create(self, values):
        return values['connection_chrono']['t_started'] / 1000

    def _get_end(self, values):
        return values['connection_chrono']['t_stopped'] / 1000

    def _get_result(self, values):
        if values['result'] != 'success':
            result = 'failure'
            if values['failureCause'] in self.canceled_causes:
                failure = 'canceled'

            elif values['failureCause'] in self.failed_causes:
                failure = 'failed'

            else:
                failure = values['failureCause']

        else:
            result = 'success'
            failure = None

        return (result, failure)

    def _get_target(self, values, is_transfer=False):
        if not is_transfer:
            if values['context'] == 'sortant':
                return values['target_display'] \
                    if values.get('target_display') else values['target']

            else:
                return values.get('caller', "unknown")
        else:
            return values['target_display_name'] \
                if values.get('target_display_name') else values['target']

    def update(self, subject):
        if subject == self.transfer_activity:
            self.compute_transfer_activity()

        else:
            self.compute_outgoing_activity()

    def compute_transfer_activity(self):
        values = self.transfer_activity.get()
        if values == 'undefined':
            log.warn(
                '[%s/%s] Received "undefined" transfer_activity.' % (
                    self.login.get(), self.session_id.get()
                )
            )
            return

        elif values:
            current_values = json.loads(values)

            current_values['target'] = current_values.get('target')
            if not current_values.get('target'):
                log.warn(
                    "[%s/%s] Can't have undefined target. values=%s" % (
                        str(values), str(self.login.get()), str(self.session_id.get()))
                )
                return

            current_activity = {
                'login': self.login.get(),
                'communication_id': current_values['parent_call_id'],
                'history_id': current_values['transfer_id'],
                'call_type': 'outbound',
                'is_transfer': True,
                'create': current_values['started'] / 1000,
                'end': current_values['ended'] / 1000,
                'failure_cause': current_values['reason'] if current_values[
                    'result'] not in ('success', 'null') else 'success',
                'target_display': self._get_target(current_values, True),
                'media': 'phone',
                'caller': current_values.get('caller', self.login.get()),
                'target': current_values['target'],
                'vocal_session_id': self.session_id.get(),
                'reason': 'success' if current_values['reason'] in (
                    None, 'null') else current_values['reason'],
                'communication_type': 'vocal',
            }

            self.set(current_activity)

    def compute_outgoing_activity(self):
        values = self.outgoing_activity.get()
        if values == 'undefined':
            log.warn(
                '[%s/%s] Received "undefined" outgoing_activity.' % (
                    self.login.get(), self.session_id.get()
                )
            )
            return

        elif values:
            current_values = json.loads(values)

            if not (current_values['context'] == "sortant" and
                    current_values['target_display'] == 'null'):

                result, failure = self._get_result(current_values)
                current_values['target'] = current_values.get('target')
                if not current_values.get('target') or not current_values.get('caller'):
                    log.warn(
                        "[%s/%s] Can't have undefined target or caller. values=%s" % (
                            str(values), self.login.get(), self.session_id.get()
                        )
                    )
                    return

                current_activity = {
                    'login': self.login.get(),
                    'communication_id': current_values['call_id'],
                    'history_id': current_values['call_id'],
                    'call_type': self._get_state(current_values),
                    # Well, its a momo bool, sorry.
                    'is_transfer': current_values['transfert'] == 'true',
                    'create': self._get_create(current_values),
                    'end': self._get_end(current_values),
                    'failure_cause': failure if result not in (
                        'success', 'null') else 'success',
                    'target_display': self._get_target(current_values),
                    'media': 'phone',
                    'caller': current_values['caller'],
                    'target': current_values['target'],
                    'vocal_session_id': self.session_id.get(),
                    'reason': 'success' if current_values[
                        'failureCause'] in (None, 'null') else current_values[
                        'failureCause'],
                    'communication_type': 'vocal'
                }

                self.set(current_activity)

    def get(self):
        return self.value


# Service basic indicators


class LatentSessionsCount(BasicIndicator):
    def __init__(self):
        super(LatentSessionsCount, self).__init__('latent_sessions_count')


class LoggedSessionsCount(BasicIndicator):
    def __init__(self):
        super(LoggedSessionsCount, self).__init__('logged_sessions_count')


class WorkingSessionsCount(BasicIndicator):
    def __init__(self):
        super(WorkingSessionsCount, self).__init__('working_sessions_count')


class WithdrawnSessionsCount(BasicIndicator):
    def __init__(self):
        super(WithdrawnSessionsCount, self).__init__(
            'withdrawn_sessions_count')


class OutboundSessionsCount(BasicIndicator):
    def __init__(self):
        super(OutboundSessionsCount, self).__init__('outbound_sessions_count')


class SupervisionSessionsCount(BasicIndicator):
    def __init__(self):
        super(SupervisionSessionsCount, self).__init__(
            'supervision_sessions_count')


class RunningTasksCount(BasicIndicator):
    def __init__(self):
        super(RunningTasksCount, self).__init__("running_tasks_count")


class ContactDurationCount(BasicIndicator):
    def __init__(self):
        super(ContactDurationCount, self).__init__(
            "contact_duration.count('0')")


class WaitingDurationCount(BasicIndicator):
    def __init__(self):
        super(WaitingDurationCount, self).__init__(
            "waiting_duration.count('0')")


class ManagedTasksCountBasic(BasicIndicator):
    def __init__(self):
        super(ManagedTasksCountBasic, self).__init__(
            "managed_tasks.count('0')")


class FailedTasksCount(BasicIndicator):
    def __init__(self):
        super(FailedTasksCount, self).__init__("failed_tasks.count('0')")


class MaxWaitingTimeThresholdCount(BasicIndicator):
    def __init__(self):
        super(MaxWaitingTimeThresholdCount, self).__init__(
            "max_waiting_time_threshold.count('0')"
        )


class MaxEstimatedWaitingTimeThresholdCount(BasicIndicator):
    def __init__(self):
        super(MaxEstimatedWaitingTimeThresholdCount, self).__init__(
            "max_estimated_waiting_time_threshold.count('0')"
        )


class NotManageableWithLatentUsersCount(BasicIndicator):
    def __init__(self):
        super(NotManageableWithLatentUsersCount, self).__init__(
            "not_manageable_with_latent_users.count('0')"
        )


class NotManageableWithoutLatentUsersCount(BasicIndicator):
    def __init__(self):
        super(NotManageableWithoutLatentUsersCount, self).__init__(
            "not_manageable_without_latent_users.count('0')"
        )


class QueueName(BasicIndicator):
    def __init__(self):
        super(QueueName, self).__init__("display_name")


class QueueTechnicalName(BasicIndicator):
    def __init__(self):
        super(QueueTechnicalName, self).__init__("name")


class MaxCurrentDurationContactTasksBasic(BasicIndicator):
    def __init__(self):
        super(MaxCurrentDurationContactTasksBasic, self).__init__(
            "oldest_contact_date"
        )


class MaxDurationContactTasksBasic(BasicIndicator):
    def __init__(self):
        super(MaxDurationContactTasksBasic, self).__init__(
            "contact_duration.max('0')"
        )


class MaxCurrentDurationWaitingTasksBasic(BasicIndicator):
    def __init__(self):
        super(MaxCurrentDurationWaitingTasksBasic, self).__init__(
            "oldest_waiting_date"
        )


class MaxDurationWaitingTasksBasic(BasicIndicator):
    def __init__(self):
        super(MaxDurationWaitingTasksBasic, self).__init__(
            "waiting_duration.max('0')"
        )

# Service advanced indicators


class UsersCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(UsersCount, self).__init__("users_count")
        self.latentSessionsCount = indicators["latent_sessions_count"]
        self.loggedSessionsCount = indicators["logged_sessions_count"]
        self.add_subject(self.latentSessionsCount)
        self.add_subject(self.loggedSessionsCount)

    def compute(self):
        self.set(
            self.latentSessionsCount.get() + self.loggedSessionsCount.get())


class AvailableUsersCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(AvailableUsersCount, self).__init__("available_users_count")
        self.loggedSessionsCount = indicators["logged_sessions_count"]
        self.workingSessionsCount = indicators["working_sessions_count"]
        self.add_subject(self.loggedSessionsCount)
        self.add_subject(self.workingSessionsCount)

    def compute(self):
        self.set(
            self.loggedSessionsCount.get() - self.workingSessionsCount.get())


class ManagingUsersCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(ManagingUsersCount, self).__init__("managing_users_count")
        self.workingSessionsCount = indicators["working_sessions_count"]
        self.add_subject(self.workingSessionsCount)

    def compute(self):
        self.set(self.workingSessionsCount.get())


class WithdrawnUsersCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(WithdrawnUsersCount, self).__init__("withdrawn_users_count")
        self.withdrawnSessionsCount = indicators['withdrawn_sessions_count']
        self.add_subject(self.withdrawnSessionsCount)

    def compute(self):
        self.set(self.withdrawnSessionsCount.get())


class OutboundUsersCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(OutboundUsersCount, self).__init__("outbound_users_count")
        self.outboundSessionsCount = indicators['outbound_sessions_count']
        self.add_subject(self.outboundSessionsCount)

    def compute(self):
        self.set(self.outboundSessionsCount.get())


class SupervisionUsersCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(SupervisionUsersCount, self).__init__("supervision_users_count")
        self.supervisionSessionsCount =\
            indicators['supervision_sessions_count']
        self.add_subject(self.supervisionSessionsCount)

    def compute(self):
        self.set(self.supervisionSessionsCount.get())


class CurrentTasksCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(CurrentTasksCount, self).__init__("current_tasks_count")
        self.runningTasksCount = indicators["running_tasks_count"]
        self.add_subject(self.runningTasksCount)

    def compute(self):
        self.set(self.runningTasksCount.get())


class WaitingTasksCount(AdvancedIndicator):
    def __init__(self, _):
        super(WaitingTasksCount, self).__init__("waiting_tasks_count")


class AverageWaitingDuration(AdvancedRateIndicator):
    def __init__(self, indicators):
        super(AverageWaitingDuration, self).__init__(
            "average_waiting_duration")
        self.waitingDurationCount = indicators["waiting_duration.count('0')"]
        self.managedTasksCount = indicators["managed_tasks.count('0')"]
        self.failedTasksCount = indicators["failed_tasks.count('0')"]
        self.add_subject(self.waitingDurationCount)
        self.add_subject(self.managedTasksCount)
        self.add_subject(self.failedTasksCount)

    def compute(self):
        self.denominator = (
            self.managedTasksCount.get() + self.failedTasksCount.get()
        )
        if self.denominator > 0:
            self.numerator = self.waitingDurationCount.get()
            self.set(self.numerator / self.denominator)


class AverageContactDuration(AdvancedRateIndicator):
    def __init__(self, indicators):
        super(AverageContactDuration, self).__init__(
            "average_processing_duration"
        )
        self.contactDurationCount = indicators["contact_duration.count('0')"]
        self.managedTasksCount = indicators["managed_tasks.count('0')"]
        self.failedTasksCount = indicators["failed_tasks.count('0')"]
        self.add_subject(self.contactDurationCount)
        self.add_subject(self.managedTasksCount)

    def compute(self):
        self.denominator = self.managedTasksCount.get()
        if self.denominator > 0:
            self.numerator = self.contactDurationCount.get()
            self.set(self.numerator / self.denominator)


class NotManageableTasksCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(NotManageableTasksCount, self).__init__(
            "not_manageable_tasks_count"
        )
        self.maxWaitingTimeThresholdCount = \
            indicators["max_waiting_time_threshold.count('0')"]
        self.maxEstimatedWaitingTimeThresholdCount = \
            indicators["max_estimated_waiting_time_threshold.count('0')"]
        self.notManageableWithLatentUsersCount = \
            indicators["not_manageable_with_latent_users.count('0')"]
        self.notManageableWithoutLatentUsersCount = \
            indicators["not_manageable_without_latent_users.count('0')"]
        self.add_subject(self.maxWaitingTimeThresholdCount)
        self.add_subject(self.maxEstimatedWaitingTimeThresholdCount)
        self.add_subject(self.notManageableWithLatentUsersCount)
        self.add_subject(self.notManageableWithoutLatentUsersCount)

    def compute(self):
        self.set(
            self.maxWaitingTimeThresholdCount.get() +
            self.maxEstimatedWaitingTimeThresholdCount.get() +
            self.notManageableWithLatentUsersCount.get() +
            self.notManageableWithoutLatentUsersCount.get()
        )


class CanceledTasksCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(CanceledTasksCount, self).__init__("canceled_tasks_count")
        self.failedTasksCount = indicators["failed_tasks.count('0')"]
        self.maxWaitingTimeThresholdCount = \
            indicators["max_waiting_time_threshold.count('0')"]
        self.maxEstimatedWaitingTimeThresholdCount = \
            indicators["max_estimated_waiting_time_threshold.count('0')"]
        self.notManageableWithLatentUsersCount = \
            indicators["not_manageable_with_latent_users.count('0')"]
        self.notManageableWithoutLatentUsersCount = \
            indicators["not_manageable_without_latent_users.count('0')"]

        self.add_subject(self.failedTasksCount)
        self.add_subject(self.maxWaitingTimeThresholdCount)
        self.add_subject(self.maxEstimatedWaitingTimeThresholdCount)
        self.add_subject(self.notManageableWithLatentUsersCount)
        self.add_subject(self.notManageableWithoutLatentUsersCount)

    def compute(self):
        self.set(
            self.failedTasksCount.get() -
            self.maxWaitingTimeThresholdCount.get() -
            self.maxEstimatedWaitingTimeThresholdCount.get() -
            self.notManageableWithLatentUsersCount.get() -
            self.notManageableWithoutLatentUsersCount.get()
        )


class ManagedTasksRate(AdvancedRateIndicator):
    def __init__(self, indicators):
        super(ManagedTasksRate, self).__init__("managed_tasks_rate")
        self.rate = True
        self.managedTasksCount = indicators["managed_tasks.count('0')"]
        self.failedTasksCount = indicators["failed_tasks.count('0')"]
        self.add_subject(self.managedTasksCount)
        self.add_subject(self.failedTasksCount)

    def _reset_value(self):
        self.numerator = 0
        self.denominator = 0
        self.value = None

    def compute(self):
        self.numerator = self.managedTasksCount.get()
        self.denominator = self.failedTasksCount.get() + self.numerator
        if self.denominator > 0:
            self.set((self.numerator / self.denominator) * 100)

        else:
            self.set(None)


class ServiceDisplayName(AdvancedIndicator):
    def __init__(self, indicators):
        super(ServiceDisplayName, self).__init__("service_display_name")
        self.displayName = indicators['display_name']
        self.add_subject(self.displayName)

    def _reset_value(self):
        pass

    def compute(self):
        if self.displayName.get():
            self.set(self.displayName.get())


class TotalTasksCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(TotalTasksCount, self).__init__("total_tasks_count")
        self.managedTasksCount = indicators["managed_tasks.count('0')"]
        self.failedTasksCount = indicators["failed_tasks.count('0')"]
        self.add_subject(self.managedTasksCount)
        self.add_subject(self.failedTasksCount)

    def compute(self):
        self.set(self.managedTasksCount.get() + self.failedTasksCount.get())


class ManagedTasksCount(AdvancedIndicator):
    def __init__(self, indicators):
        super(ManagedTasksCount, self).__init__("managed_tasks_count")
        self.managedTasksCount = indicators["managed_tasks.count('0')"]
        self.add_subject(self.managedTasksCount)

    def compute(self):
        self.set(self.managedTasksCount.get())


class MaxCurrentDurationContactTasks(AdvancedIndicator):
    def __init__(self, indicators):
        super(MaxCurrentDurationContactTasks, self).__init__(
            "max_current_duration_processing_tasks"
        )
        self.maxCurrentDurationContactTasks = indicators['oldest_contact_date']
        self.add_subject(self.maxCurrentDurationContactTasks)

    def compute(self):
        value = self.maxCurrentDurationContactTasks.get()
        if value:
            self.set(date_to_iso(value))
        else:
            self.set("stop")


class MaxDurationContactTasks(AdvancedIndicator):
    def __init__(self, indicators):
        super(MaxDurationContactTasks, self).__init__(
            "max_duration_processing_tasks"
        )
        self.maxDurationContactTasks = indicators["contact_duration.max('0')"]
        self.add_subject(self.maxDurationContactTasks)

    def compute(self):
        self.set(self.maxDurationContactTasks.get())

    def set(self, value):
        if value is None:
            self.reset()
            return

        if value == "":
            value = 0

        if value != self.value:
            self.value = value
        # Little variation of set() from BasicIndicator
        self.notify()


class MaxCurrentDurationWaitingTasks(AdvancedIndicator):
    def __init__(self, indicators):
        super(MaxCurrentDurationWaitingTasks, self).__init__(
            "max_current_duration_waiting_tasks")
        self.maxCurrentDurationWaitingTasks = indicators['oldest_waiting_date']
        self.add_subject(self.maxCurrentDurationWaitingTasks)

    def compute(self):
        value = self.maxCurrentDurationWaitingTasks.get()
        if value:
            self.set(date_to_iso(value))
        else:
            self.set("stop")


class MaxDurationWaitingTasks(AdvancedIndicator):
    def __init__(self, indicators):
        super(MaxDurationWaitingTasks, self).__init__(
            "max_duration_waiting_tasks")
        self.maxDurationWaitingTasks = indicators["waiting_duration.max('0')"]
        self.add_subject(self.maxDurationWaitingTasks)

    def compute(self):
        self.set(self.maxDurationWaitingTasks.get())

    def set(self, value):
        if value is None:
            self.reset()
            return

        if value == "":
            value = 0

        if value != self.value:
            self.value = value
        # Little variation of set() from BasicIndicator
        self.notify()


# Call's basic indicators


class CallId(BasicIndicator):
    def __init__(self):
        super(CallId, self).__init__("session_id")


class TaskId(BasicIndicator):
    def __init__(self):
        super(TaskId, self).__init__("task_id")


class CallStartDate(BasicIndicator):
    def __init__(self):
        super(CallStartDate, self).__init__("start_date")


class CallEndDate(BasicIndicator):
    def __init__(self):
        super(CallEndDate, self).__init__("end_date")


class CallStopWaitingDate(BasicIndicator):
    def __init__(self):
        super(CallStopWaitingDate, self).__init__("stop_waiting_date")


class CallManagementDate(BasicIndicator):
    def __init__(self):
        super(CallManagementDate, self).__init__("management_date")


class CallPostManagementDate(BasicIndicator):
    def __init__(self):
        super(CallPostManagementDate, self).__init__("post_management_date")


class CallUserLogin(BasicIndicator):
    def __init__(self):
        super(CallUserLogin, self).__init__("manager_session.user.login")


class CallProfileName(BasicIndicator):
    def __init__(self):
        super(CallProfileName, self).__init__("manager_session.profile_name")


class QueueType(BasicIndicator):
    def __init__(self):
        super(QueueType, self).__init__("queue_type")


class QueueDisplayName(BasicIndicator):
    def __init__(self):
        super(QueueDisplayName, self).__init__("queue_display_name")


class LocalNumber(BasicIndicator):
    def __init__(self):
        super(LocalNumber, self).__init__('attributes.local_number.value')


class RemoteNumber(BasicIndicator):
    def __init__(self):
        super(RemoteNumber, self).__init__('attributes.remote_number.value')


class SessionCreateDate(BasicIndicator):
    def __init__(self):
        super(SessionCreateDate, self).__init__('create_date')


class SessionTerminateDate(BasicIndicator):
    def __init__(self):
        super(SessionTerminateDate, self).__init__('terminate_date')


class PreviousQueue(BasicIndicator):
    def __init__(self):
        super(PreviousQueue, self).__init__('previous_queue')

    def _reset_value(self):
        self.value = None


class PreviousProfile(BasicIndicator):
    def __init__(self):
        super(PreviousProfile, self).__init__('previous_profile')

    def _reset_value(self):
        self.value = None

# Call's advanced indicators


class CallIdentifier(AdvancedIndicator):
    def __init__(self, indicators):
        super(CallIdentifier, self).__init__("call_id")
        self.callId = indicators['session_id']
        self.add_subject(self.callId)

    def compute(self):
        self.set(self.callId.get())


class CommunicationTaskId(AdvancedIndicator):
    def __init__(self, indicators):
        super(CommunicationTaskId, self).__init__("communication_task_id")
        self.taskId = indicators['task_id']
        self.add_subject(self.taskId)

    def compute(self):
        self.set(self.taskId.get())


class TaskIdentifier(AdvancedIndicator):
    def __init__(self, indicators):
        super(TaskIdentifier, self).__init__("task_id")
        self.callEndDate = indicators['end_date']
        self.taskId = indicators['task_id']
        self.add_subject(self.taskId)
        self.initialized = False

    def _reset_value(self):
        super(TaskIdentifier, self)._reset_value()

    def compute(self):
        if not self.initialized:
            self.set(self.taskId.get())
            self.initialized = True

        else:
            if self.taskId.get():
                self.callEndDate.set(date_to_iso())
                self.set(self.taskId.get())


class WaitingDuration(AdvancedIndicator):
    def __init__(self, indicators):
        super(WaitingDuration, self).__init__("waiting_duration")
        self.start = indicators['start_date']
        self.end = indicators['stop_waiting_date']
        self.add_subject(self.start)
        self.add_subject(self.end)

    def _reset_value(self):
        self.value = None

    def compute(self):
        start = self.start.get()
        end = self.end.get()

        if start and end and end > start:
            value = (end - start).seconds
            self.set(value)


class IsWaiting(AdvancedIndicator):
    def __init__(self, indicators):
        super(IsWaiting, self).__init__('is_waiting')
        self.end = indicators['stop_waiting_date']
        self.add_subject(self.end)
        self.value = True

    def compute(self):
        if self.end.get() not in ['', None, 0, "0"]:
            self.set(False)
        else:
            self.set(True)


class ManagingDuration(AdvancedIndicator):
    def __init__(self, indicators):
        super(ManagingDuration, self).__init__("managing_duration")
        self.start = indicators['management_date']
        self.add_subject(self.start)

    def _reset_value(self):
        self.value = None

    def compute(self):
        start = self.start.get()
        if start:
            if type(start) == str:
                self.set(start)
            else:
                self.set(start.isoformat())


class CreateDate(AdvancedIndicator):
    def __init__(self, indicators):
        super(CreateDate, self).__init__("communication_create_date")
        self.createDate = indicators['create_date']
        self.add_subject(self.createDate)

    def compute(self):
        value = self.createDate.get()
        if type(value) == str:
            if value != 'stop':
                self.set(value)
        else:
            self.set(self.createDate.get().isoformat())


class StartDate(AdvancedIndicator):
    def __init__(self, indicators):
        super(StartDate, self).__init__('task_start_date')
        self.callStartDate = indicators['start_date']
        self.add_subject(self.callStartDate)

    def _reset_value(self):
        super(StartDate, self)._reset_value()
        self.initialized = False

    def compute(self):
        if not self.initialized:
            try:
                start = self.callStartDate.get()
                if start:
                    if type(start) == str:
                        self.set(start)
                    else:
                        self.set(str(date_to_iso(start)))
                else:
                    self.set("")

            except TypeError:
                self.set("")

            self.initialized = True


class TotalDuration(AdvancedIndicator):
    def __init__(self, indicators):
        super(TotalDuration, self).__init__("total_duration")
        self.waiting_start = indicators['start_date']
        self.add_subject(self.waiting_start)

    def _reset_value(self):
        self.value = None

    def compute(self):
        start = self.waiting_start.get()
        if start:
            if type(start) == str:
                self.set(start)
            else:
                self.set(start.isoformat())


class CommunicationChannel(AdvancedIndicator):
    def __init__(self, indicators):
        super(CommunicationChannel, self).__init__("channel")
        self.value = "iv-vocal"

    def _reset_value(self):
        self.value = "iv-vocal"

    def get(self):
        return self.value


class EndDate(AdvancedIndicator):
    def __init__(self, indicators):
        super(EndDate, self).__init__('task_end_date')

        self.callEndDate = indicators['end_date']
        self.sessionTerminateDate = indicators['terminate_date']
        self.add_subject(self.callEndDate)
        self.add_subject(self.sessionTerminateDate)

    def compute(self):
        try:
            end = self.callEndDate.get()
            terminate = self.sessionTerminateDate.get()
            if terminate:
                self.set(str(date_to_iso(terminate)))
                return
            if end:
                if type(end) == str:
                    self.set(end)
                else:
                    self.set(str(date_to_iso(end)))
            else:
                self.set("")

        except TypeError:
            self.set("")


class CurrentAgentName(AdvancedIndicator):
    def __init__(self, indicators):
        super(CurrentAgentName, self).__init__('current_agent_name')
        self.callUserLogin = indicators['manager_session.user.login']
        self.add_subject(self.callUserLogin)

    def compute(self):
        self.set(self.callUserLogin.get())


class InitialAgentName(AdvancedIndicator):
    def __init__(self, indicators):
        super(InitialAgentName, self).__init__('initial_agent_name')
        self.callUserLogin = indicators['manager_session.user.login']
        self.add_subject(self.callUserLogin)

    def _reset_value(self):
        self.value = None
        self.initialized = False

    def compute(self):
        if not self.initialized and self.callUserLogin.get():
            self.set(self.callUserLogin.get())
            self.initialized = True


class CallProfile(AdvancedIndicator):
    def __init__(self, indicators):
        super(CallProfile, self).__init__('call_profile')
        self.callProfileName = indicators['manager_session.profile_name']
        self.previousProfile = indicators['previous_profile']
        self.add_subject(self.callProfileName)
        self.initialized = False

    def compute(self):
        if not self.initialized and self.callProfileName.get():
            self.initialized = True

        elif self.value != self.callProfileName.get() and \
                self.callProfileName.get():
            self.previousProfile.set(self.value)

        self.set(self.callProfileName.get())


class PreviousProfileName(AdvancedIndicator):
    def __init__(self, indicators):
        super(PreviousProfileName, self).__init__('previous_profile_name')
        self.previousProfile = indicators['previous_profile']
        self.add_subject(self.previousProfile)

    def _reset_value(self):
        self.value = None

    def compute(self):
        self.set(self.previousProfile.get())

    def get(self):
        return {self.name: self.value}


class CurrentQueueName(AdvancedIndicator):
    def __init__(self, indicators):
        super(CurrentQueueName, self).__init__("current_queue_name")

        self.queueType = indicators['queue_type']
        self.queueDisplayName = indicators['queue_display_name']
        self.callUserLogin = indicators[
            'manager_session.user.login'
        ]
        self.previousQueue = indicators['previous_queue']

        self.add_subject(self.queueType)
        self.add_subject(self.queueDisplayName)
        self.add_subject(self.callUserLogin)
        self.initialized = False

    def compute(self):
        if self.queueType.get() == 'queue' and self.queueDisplayName.get():
            if not self.initialized and self.queueDisplayName.get():
                self.initialized = True

            elif self.value != self.queueDisplayName.get() and \
                    self.queueDisplayName.get():
                self.previousQueue.set(self.value)
            self.set(self.queueDisplayName.get())

        elif self.callUserLogin.get():
            if not self.initialized and self.callUserLogin.get():
                self.initialized = True

            elif self.value != self.callUserLogin.get() and \
                    self.callUserLogin.get():
                self.previousQueue.set(self.value)
            self.set(self.callUserLogin.get())


class PreviousQueueName(AdvancedIndicator):
    def __init__(self, indicators):
        super(PreviousQueueName, self).__init__("previous_queue_name")
        self.previousQueue = indicators['previous_queue']
        self.add_subject(self.previousQueue)

    def _reset_value(self):
        self.value = None

    def compute(self):
        self.set(self.previousQueue.get())

    def get(self):
        return {self.name: self.value}


class InitialQueueName(AdvancedIndicator):
    def __init__(self, indicators):
        super(InitialQueueName, self).__init__("initial_queue_name")
        self.queueType = indicators['queue_type']
        self.queueDisplayName = indicators['queue_display_name']
        self.callUserLogin = indicators['manager_session.user.login']

        # QueueDisplayName is the last to be updated
        # adding others may cause bad value.
        self.add_subject(self.queueDisplayName)

    def _reset_value(self):
        self.value = None
        self.initialized = False

    def compute(self):
        if not self.initialized:
            if self.queueType.get() == 'queue' and self.queueDisplayName.get():
                self.set(self.queueDisplayName.get())
                self.initialized = True

            elif self.callUserLogin.get():
                self.set(self.callUserLogin.get())
                self.initialized = True


class Entrypoint(AdvancedIndicator):
    def __init__(self, indicators):
        super(Entrypoint, self).__init__("to")
        self.localNumber = indicators['attributes.local_number.value']
        self.add_subject(self.localNumber)

    def compute(self):
        self.set(self.localNumber.get())

    def get(self):
        try:
            return {
                self.name: {'value': self.value.split(':')[1].split('@')[0]}
            }

        except:
            return super(Entrypoint, self).get()


class Origin(AdvancedIndicator):
    def __init__(self, indicators):
        super(Origin, self).__init__('from')
        self.remoteNumber = indicators['attributes.remote_number.value']
        self.add_subject(self.remoteNumber)

    def compute(self):
        self.set(self.remoteNumber.get())

    def get(self):
        try:
            return {
                self.name: {'value': self.value.split(':')[1].split('@')[0]}
            }

        except:
            return super(Origin, self).get()


class CommunicationEntrypoint(AdvancedIndicator):
    def __init__(self, indicators):
        super(CommunicationEntrypoint, self).__init__('to')

    def set(self, value):
        super(CommunicationEntrypoint, self).set(value['value'])


class CommunicationOrigin(AdvancedIndicator):
    def __init__(self, indicators):
        super(CommunicationOrigin, self).__init__('from')

    def set(self, value):
        super(CommunicationOrigin, self).set(value['value'])


class CommunicationCreateDate(AdvancedIndicator):
    def __init__(self, indicators):
        super(CommunicationCreateDate, self).__init__(
            'communication_create_date'
        )

    def set(self, value):
        super(CommunicationCreateDate, self).set(value['value'])
