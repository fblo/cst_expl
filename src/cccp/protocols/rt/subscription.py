#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from copy import deepcopy
from twisted.internet import reactor

from ivcommons.dictionaries import InstanciatorDictionary
from ivcommons.log import Log
from ivcommons.patterns.observer import (
    Observer,
    Subject,
)

from cccp.protocols.rt.indicators import (
    # Session indicator
    TotalInboundCount,
    ManagedInboundCount,
    LostInboundCount,
    TaskStateContactDuration,
    UserContactDurationMaxBasic,
    RedirectedInboundCount,
    TransferredInboundCount,
    UserHoldDurationMaxBasic,
    TaskStateHeldDuration,
    TaskStateRingingDuration,
    UserRingingDurationMaxBasic,
    TotalOutboundDuration,
    TotalWithdrawalDuration,
    ProfileName,
    DisplayName,
    Mode,
    LastLoginDate,
    TaskManagedStartDate,
    TaskManagedEndDate,
    VocalState,
    SessionLogged,
    BusyCount,
    LastRecord,
    RecordActive,
    CurrentSpies,
    VocalStateDisplayName,
    PhoneURI,
    Login,
    VocalStateStartDate,
    UserTotalTasksCount,
    UserManagedTasksCount,
    UserLostTasksCount,
    UserAverageContactDuration,
    UserMaxContactDuration,
    UserTransferredTasks,
    UserMaxHoldDuration,
    UserAverageHoldDuration,
    UserMaxRingingDuration,
    UserAverageRingingDuration,
    UserVocalTotalOutboundDuration,
    UserVocalTotalWithdrawalDuration,
    UserProfileName,
    UserDisplayName,
    UserVocalTotalNamedWithdrawalDuration,
    UserVocalMode,
    SessionLastLoginDate,
    UserCurrentTaskManagedDate,
    UserVocalState,
    SessionId,
    IsLogged,
    AutoRecordSessionWatcher,
    RecordIndicator,
    RecordEnabled,
    SessionCurrentSpies,
    Interface,
    UserVocalPosition,
    TaskStartDate,
    UserCurrentTaskStartDate,
    UserVocalStateStartDate,
    UserLogin,
    UserRawVocalState,
    TotalLegCount,
    UserTotalLegCount,
    ContactedLegCount,
    UserContactedLegCount,
    FailedLegCount,
    UserFailedLegCount,
    CanceledLegCount,
    UserCanceledLegCount,
    OutboundContactDuration,
    OutboundMaxContactDuration,
    UserOutboundContactTotalDuration,
    UserOutboundContactMaxDuration,
    UserOutboundContactAverageDuration,
    CallId,
    OutboundState,
    OutboundHoldState,
    LastOutboundCallStart,
    LastOutgoingActivity,
    LastTransferActivity,
    UserActivity,
    StateStartDate,
    StateStartTime,
    # Service indicator
    LatentSessionsCount,
    LoggedSessionsCount,
    WorkingSessionsCount,
    RunningTasksCount,
    WaitingTasksCount,
    ManagedTasksCountBasic,
    FailedTasksCount,
    MaxWaitingTimeThresholdCount,
    ContactDurationCount,
    WaitingDurationCount,
    MaxEstimatedWaitingTimeThresholdCount,
    NotManageableWithLatentUsersCount,
    NotManageableWithoutLatentUsersCount,
    QueueName,
    QueueTechnicalName,
    MaxCurrentDurationContactTasksBasic,
    MaxDurationContactTasksBasic,
    MaxCurrentDurationWaitingTasksBasic,
    MaxDurationWaitingTasksBasic,
    UsersCount,
    AvailableUsersCount,
    ManagingUsersCount,
    CurrentTasksCount,
    AverageContactDuration,
    AverageWaitingDuration,
    NotManageableTasksCount,
    CanceledTasksCount,
    ManagedTasksRate,
    ServiceDisplayName,
    TotalTasksCount,
    ManagedTasksCount,
    MaxCurrentDurationContactTasks,
    MaxDurationContactTasks,
    MaxCurrentDurationWaitingTasks,
    MaxDurationWaitingTasks,
    VocalSessionId,
    VocalInterface,
    WithdrawnSessionsCount,
    WithdrawnUsersCount,
    OutboundSessionsCount,
    OutboundUsersCount,
    SupervisionSessionsCount,
    SupervisionUsersCount,
    # Call indicator
    CallRecordIndicator,
    CallStartDate,
    CallEndDate,
    CallStopWaitingDate,
    CallManagementDate,
    CallPostManagementDate,
    CallUserLogin,
    CallProfileName,
    QueueType,
    QueueDisplayName,
    LocalNumber,
    RemoteNumber,
    PreviousQueue,
    PreviousProfile,
    SessionCreateDate,
    SessionTerminateDate,
    WaitingDuration,
    ManagingDuration,
    TotalDuration,
    CommunicationChannel,
    CreateDate,
    StartDate,
    EndDate,
    TaskId,
    InitialAgentName,
    CurrentAgentName,
    CallProfile,
    CurrentQueueName,
    InitialQueueName,
    Entrypoint,
    Origin,
    CommunicationEntrypoint,
    CommunicationOrigin,
    CommunicationCreateDate,
    CommunicationTaskId,
    PreviousQueueName,
    PreviousProfileName,
    IsWaiting,
)

log = Log('cccp.protocols.rt.subscription')


class Subscribable(Subject, Observer, object):
    def __init__(self):
        super(Subscribable, self).__init__()
        super(Subscribable, self).__init__()
        self.indicators = {}
        self.subjects = []

    def add_indicator(self, indicator):
        if indicator.name in self.indicators:
            raise LookupError(
                "Indicator %s already exists" % (
                    indicator.name,
                )
            )

        else:
            self.indicators[indicator.name] = indicator
            if indicator.subscribable:
                self.subjects.append(indicator)
                indicator.attach(self)

    def del_indicator(self, name):
        if name not in self.indicators:
            raise LookupError(
                "Indicator %s not found" % (
                    name,
                )
            )
        else:
            del self.indicators[name]

    def get_indicator(self, name):
        return self.indicators[name]

    def has_indicator(self, name):
        return name in self.indicators

    def apply_data(self, data):
        for indicator_name in self.indicators:
            if indicator_name in data:
                self.indicators[indicator_name].set(data[indicator_name])

    def update(self, subject):
        raise NotImplementedError()

    def reset(self):
        for indicator in self.indicators.values():
            indicator.reset()


class Profile(Subscribable):
    def __init__(self, name, indicator_lut):
        super(Profile, self).__init__()
        self.name = name
        self.sessions = InstanciatorDictionary(Session)
        self.subjects = []
        self.values = []
        self.deferredCall = None
        self.indicator_lut = indicator_lut

        self.subscribable_indicators = {
            'session': [
                'user_display_name',
                'user_profile_name',
                'user_vocal_state',
                'vocal_session_last_login_date',
                'user_vocal_mode',
                'user_vocal_total_withdrawal_duration',
                'user_vocal_total_outbound_duration',
                'user_total_tasks_count',
                'user_lost_tasks_count',
                'user_transferred_tasks',
                'user_max_duration_ringing_tasks',
                'user_max_duration_contact_tasks',
                'user_max_duration_hold_tasks',
                'user_average_ringing_duration',
                'user_average_contact_duration',
                'user_average_hold_duration',
                'vocal_user_current_task_start_date',
                'vocal_session_id',
                'is_logged',
                'record_enabled',
                'vocal_interface',
                'user_managed_tasks_count',
                'user_vocal_position',
                'vocal_state_start_time',
                'current_spies',
                'user_total_leg_count',
                'user_contacted_leg_count',
                'user_failed_leg_count',
                'user_canceled_leg_count',
                'user_outbound_contact_total_duration',
                'user_outbound_contact_maximum_duration',
                'user_outbound_contact_average_duration',
            ],
        }

        self.indicators = {'session': []}

    def reset(self, log=log):
        session_count = 0
        for session in self.sessions.values():
            session.reset()
            session_count += 1

        log.system_message(
            'CCCP - [%s] Resetting values for %d sessions.' % (
                self.name, session_count
            )
        )

    def add_indicator(self, name, _type):
        if name not in self.indicators[_type]:
            if name in self.subscribable_indicators[_type]:
                self.indicators[_type].append(name)

            elif name.startswith('user_vocal_total_named') and \
                    name.endswith('withdrawal_duration'):
                self.indicators[_type].append(name)

            else:
                raise LookupError(
                    "Indicator %s not subscribable." % (
                        name
                    )
                )
        else:
            raise LookupError(
                "Indicator %s already subscribed." % (
                    name
                )
            )

    def del_indicator(self, name, _type):
        if name in self.indicators[_type]:
            self.indicators[_type].remove(name)

        else:
            raise LookupError(
                "Indicator %s not subscribed"
            )

    def has_indicator(self, name, _type):
        return name in self.indicators[_type]

    def add_session(self, name):
        if name in self.sessions:
            raise LookupError(
                "Session %s already exists in %s" % (
                    name,
                    self.name,
                )
            )

        else:
            self.sessions[name] = Session(name, self.indicator_lut)
            self.indicator_lut.update_autorecord_subscription(
                self.sessions[name].get_indicator('autorecord_session_watcher')
            )
            self.indicator_lut.update_record_subscription(
                self.sessions[name].get_indicator('record_indicator')
            )
            self.indicator_lut.update_history_subscription(
                self.sessions[name].get_indicator('user_activity')
            )
            self.add_subject(self.sessions[name])
            self.sessions[name].update_listenable_indicators(
                self.indicators['session']
            )
            return self.sessions[name]

    def del_session(self, name):
        if name not in self.sessions:
            raise LookupError(
                "Session %s not found in %s" % (
                    name,
                    self.name,
                )
            )
        else:
            self.del_subject(self.sessions[name])
            del self.sessions[name]

    def get_session(self, name):
        if name not in self.sessions:
            self.add_session(name)
            session = self.sessions[name]

        else:
            session = self.sessions[name]
            session.update_listenable_indicators(
                self.indicators['session']
            )
        return session

    def add_subject(self, subject):
        self.subjects.append(subject)
        subject.attach(self)

    def del_subject(self, subject):
        self.subjects.remove(subject)
        subject.detach(self)

    def update(self, subject):
        data = subject.get()
        if 'is_logged' in data:
            if not data['is_logged']['value']:
                self.del_session(data['login'])

        self.values.append(data)
        if not self.deferredCall:
            self.deferredCall = reactor.callLater(
                0.1,
                self.delayedNotification
            )

    def delayedNotification(self):
        self.notify()
        self.values = []
        self.deferredCall = None

    def get(self):
        return self.values

    def get_values(self, _type, indicators_filtered=[], is_api=False):
        values = []
        for subject in self.subjects:
            if _type == subject.object_type:
                values.append(subject.get_values(
                    indicators_filtered, is_api=is_api)
                )

        return values

    def get_session_list(self):
        user_list = []
        for session in self.sessions:
            if self.sessions[session].indicators['is_logged'].value:
                user_list.append(
                    {
                        'login': session,
                        'display_name': self.sessions[
                            session].display_name.get()
                    }
                )

        return user_list


class Communication(Subscribable):
    def __init__(self, name, clistener, communication_type='inbound'):
        super(Communication, self).__init__()
        self.name = name
        self.subjects = []
        self.tasks = []
        self.communication_type = communication_type
        self.values = {
            'communication_id': self.name,
            'communication_task_id': {'value': None},
            'channel': {'value': 'iv-vocal'},
            'communication_type': {'value': self.communication_type},
            'new': True
        }
        self.deferredCall = None

        self.object_type = "communication"

        # Basic indicators
        basic_indicators = [
            CallProfileName, QueueType, QueueDisplayName, CallUserLogin,
            LocalNumber, RemoteNumber, SessionCreateDate, SessionTerminateDate,
            CallEndDate, PreviousQueue, PreviousProfile,
            LastRecord, RecordActive
        ]

        for basic_indicator in basic_indicators:
            self.add_indicator(basic_indicator())

        # Advanced Indicators
        adv_indicators = [
            CurrentQueueName, CallProfile,
            Entrypoint, Origin, CreateDate,
            EndDate, PreviousQueueName, PreviousProfileName,
            RecordEnabled, CallRecordIndicator
        ]

        for adv_indicator in adv_indicators:
            self.add_indicator(adv_indicator(self.indicators))

        self.current_queue = self.indicators['current_queue_name']
        self.current_profile = self.indicators['call_profile']
        self.previous_queue = self.indicators['previous_queue_name']
        self.previous_profile = self.indicators['previous_profile_name']

        self.initial_queue_name = None
        self.initial_agent_name = None

        self.clistener = clistener

    def has_tasks(self):
        return bool(self.tasks)

    def remove_task(self, task_id):
        for task in self.tasks:
            if task_id == task.task_id.value:
                self.unbind_task(task)
                return True

        return False

    def clean_tasks(self):
        for task in self.tasks:
            self.unbind_task(task)

    def get_task_ids(self):
        ids = []
        for task in self.tasks:
            ids.append(task.task_id.value)
        return ids

    def check_end_scope(self, queue_scope, profile_scope):
        comm_scope = False
        end = None
        for task in self.tasks:
            in_scope, task_end = task.check_end_scope(
                queue_scope, profile_scope
            )
            if in_scope:
                comm_scope = True
                if not task_end:
                    return (True, None)

                else:
                    end = task_end

        return (comm_scope, end)

    def check_scope(self, queue_scope, profile_scope):
        for task in self.tasks:
            if task.check_scope(queue_scope, profile_scope):
                return True

        return False

    def get(self):
        return deepcopy({
            'data': self.values,
            'current_queue_name': self.current_queue.value,
            'current_profile_name': self.current_profile.value,
            'previous_queue_name': self.previous_queue.value,
            'previous_profile_name': self.previous_profile.value,
            'is_waiting': True,
        })

    def get_values(self, indicators_filtered=[], **kwargs):
        values = {
            'communication_id': self.name,
            'communication_task_id': {'value': None},
            'communication_type': {'value': self.communication_type},
            'channel': {'value': 'iv-vocal'}
        }
        for indicator in self.indicators:
            if self.indicators[indicator].is_advanced:
                if indicators_filtered:
                    if indicator in indicators_filtered:
                        values.update(self.indicators[indicator].get())

                else:
                    values.update(self.indicators[indicator].get())

        return deepcopy({
            'data': values,
            'current_queue_name': self.current_queue.value,
            'current_profile_name': self.current_profile.value,
            'previous_queue_name': self.previous_queue.value,
            'previous_profile_name': self.previous_profile.value,
            'is_waiting': True,
        })

    def update(self, subject):
        if self.tasks:
            indicator = subject.get()
            for task in self.tasks:
                if 'to' in indicator:
                    task.indicators['to'].set(indicator['to'])

                if 'from' in indicator:
                    task.indicators['from'].set(indicator['from'])

                if 'record_indicator' in indicator:
                    task.indicators['record_indicator'].set(
                        indicator['record_indicator']
                    )

                if 'record_enabled' in indicator:
                    task.indicators['record_enabled'].set(
                        indicator['record_enabled']
                    )
        else:
            self.values.update(subject.get())
            if not self.deferredCall:
                self.deferredCall = reactor.callLater(
                    0.3,
                    self.delayedNotification
                )

    def delayedNotification(self):
        self.notify()
        self.values = {
            'communication_id': self.name,
            'communication_task_id': {'value': None},
            'communication_type': {'value': self.communication_type},
            'channel': {'value': 'iv-vocal'}
        }
        self.deferredCall = None

    def validate_task(self, task, values):
        if len(self.tasks) > 1:
            if self.tasks[0] == task:
                # First task
                if task.current_profile.value == self.tasks[
                        1].current_profile.value:
                    # Same profile
                    # Just send the values of the second task instead
                    # of current values
                    values = self.tasks[1].get_values()
                    self.unbind_task(task)
                    return values

                else:
                    # Different profile
                    return values

            else:
                # Second task starting
                if task.current_profile.value == self.tasks[
                        0].current_profile.value:
                    if task.indicators['task_end_date'].value:
                        self.unbind_task(task)
                    # Same profile
                    # Dont send values to avoid overide first task update
                    return {}

                else:
                    # Different profile
                    if not task.current_profile.value and \
                            task.indicators['task_end_date'].value:
                        self.unbind_task(task)

                    return values

        else:
            return values

    def bind_task(self, task):
        if task not in self.tasks:
            self.tasks.append(task)
            if len(self.tasks) > 1:
                values = self.tasks[0].get_values(
                    ['initial_agent_name', 'initial_queue_name',
                     'current_agent_name']
                )['data']
                task.force_update(values)

        if not self.initial_queue_name and task.indicators[
                'initial_queue_name'].value:
            self.initial_queue_name = task.indicators[
                'initial_queue_name'].value

        if not self.initial_agent_name and task.indicators[
                'initial_agent_name'].value:
            self.initial_agent_name = task.indicators[
                'initial_agent_name'].value

        if self.initial_queue_name:
            task.indicators['initial_queue_name'].initialized = True
            task.indicators['initial_queue_name'].set(self.initial_queue_name)

        if self.initial_agent_name:
            task.indicators['initial_agent_name'].initialized = True
            task.indicators['initial_agent_name'].set(self.initial_agent_name)

    def unbind_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
            self.clistener.del_task(task.task_id.value)

    def is_task(self):
        return False


class Task(Subscribable):
    def __init__(self, call_id, data, communication_data,
                 communication_type="inbound"):

        super(Task, self).__init__()

        self.call_id = call_id

        self.subjects = []

        self.communication_type = communication_type

        self.values = {
            'communication_id': self.call_id,
            'channel': {'value': 'iv-vocal'},
            'communication_type': {'value': self.communication_type}
        }

        if communication_data.get('new', None):
            self.values['new'] = True

        self.deferredCall = None

        self.object_type = "communication"

        # Basic indicators
        basic_indicators = [
            CallStartDate, CallEndDate, CallManagementDate,
            CallPostManagementDate, CallStopWaitingDate,
            CallUserLogin, CallProfileName, QueueType,
            QueueDisplayName, TaskId, SessionTerminateDate,
            PreviousQueue, PreviousProfile,
            LastRecord, RecordActive
        ]

        for basic_indicator in basic_indicators:
            self.add_indicator(basic_indicator())

        # Advanced indicators
        adv_indicators = [
            WaitingDuration, ManagingDuration, TotalDuration,
            CommunicationChannel, StartDate, EndDate,
            CallProfile, InitialAgentName, CurrentAgentName,
            InitialQueueName, CurrentQueueName,
            CommunicationEntrypoint, CommunicationOrigin,
            CommunicationCreateDate, CommunicationTaskId,
            PreviousQueueName, PreviousProfileName,
            IsWaiting, RecordEnabled, CallRecordIndicator
        ]

        for adv_indicator in adv_indicators:
            self.add_indicator(adv_indicator(self.indicators))

        self.current_queue = self.indicators['current_queue_name']
        self.current_profile = self.indicators['call_profile']
        self.previous_queue = self.indicators['previous_queue_name']
        self.previous_profile = self.indicators['previous_profile_name']
        self.is_waiting = self.indicators['is_waiting']
        self.task_id = self.indicators['communication_task_id']

        self.apply_data(data)
        self.apply_data(communication_data)

        if 'communication_task_id' not in self.values:
            self.values['communication_task_id'] = {
                'value': self.task_id.value
            }

    def check_end_scope(self, queue_scope, profile_scope):
        if self.check_scope(queue_scope, profile_scope):
            return (True, self.indicators['task_end_date'].value)

        else:
            return (False, None)

    def check_scope(self, queue_scope, profile_scope):
        if self.current_profile.value:
            return self.current_profile.value in profile_scope
        else:
            return self.current_queue.value in queue_scope

    def get(self):
        return deepcopy({
            'data': self.values,
            'current_queue_name': self.current_queue.value,
            'current_profile_name': self.current_profile.value,
            'previous_queue_name': self.previous_queue.value,
            'previous_profile_name': self.previous_profile.value,
            'is_waiting': self.is_waiting.value
        })

    def get_values(self, indicators_filtered=[], **kwargs):
        values = {
            'communication_id': self.call_id,
            'communication_task_id': {'value': self.task_id.value},
            'channel': {'value': 'iv-vocal'},
            'communication_type': {'value': self.communication_type}
        }
        for indicator in self.indicators:
            if self.indicators[indicator].is_advanced:
                if indicators_filtered:
                    if indicator in indicators_filtered:
                        values.update(self.indicators[indicator].get())
                else:
                    values.update(self.indicators[indicator].get())

        return deepcopy({
            'data': values,
            'current_queue_name': self.current_queue.value,
            'current_profile_name': self.current_profile.value,
            'previous_queue_name': self.previous_queue.value,
            'previous_profile_name': self.previous_profile.value,
            'is_waiting': self.is_waiting.value
        })

    def update(self, subject):
        self.values.update(subject.get())
        if not self.deferredCall:
            self.deferredCall = reactor.callLater(0.5,
                                                  self.delayedNotification)

    def force_update(self, values):
        del values['communication_task_id']
        del values['communication_id']
        del values['channel']
        del values['communication_type']
        for indicator in values:
            self.indicators[indicator].set(values[indicator]['value'])

    def delayedNotification(self):
        if 'communication_task_id' not in self.values:
            self.values['communication_task_id'] = {
                'value': self.task_id.value
            }

        self.notify()
        self.values = {
            'communication_id': self.call_id,
            'communication_task_id': {'value': self.task_id.value},
            'channel': {'value': 'iv-vocal'},
            'communication_type': {'value': self.communication_type}
        }
        self.deferredCall = None

    def is_task(self):
        return True


class Session(Subscribable):
    def __init__(self, name, indicator_lut):
        super(Session, self).__init__()
        self.name = name
        self.subjects = []
        self.values = {'login': self.name}
        self.deferredCall = None
        self.object_type = "session"
        self.listenable_indicators = {}
        self.display_name = DisplayName()
        self.add_indicator(self.display_name)
        self.indicator_lut = indicator_lut

        # Basic indicators
        basic_indicators = [
            UserContactDurationMaxBasic,
            TaskStateContactDuration, RedirectedInboundCount,
            TransferredInboundCount, UserHoldDurationMaxBasic,
            TaskStateHeldDuration, UserRingingDurationMaxBasic,
            TaskStateRingingDuration, TotalInboundCount,
            ManagedInboundCount, LostInboundCount,
            TotalWithdrawalDuration, ProfileName,
            Mode, LastLoginDate, TotalOutboundDuration,
            TaskManagedStartDate, TaskManagedEndDate,
            VocalState, SessionId, SessionLogged, BusyCount,
            LastRecord, VocalStateDisplayName, RecordActive,
            Interface, PhoneURI, Login, TaskStartDate, StateStartDate,
            VocalStateStartDate, CurrentSpies, TotalLegCount,
            ContactedLegCount, FailedLegCount, CanceledLegCount,
            OutboundContactDuration, OutboundMaxContactDuration,
            CallId, OutboundState, OutboundHoldState,
            LastOutboundCallStart, LastOutgoingActivity,
            LastTransferActivity,
        ]

        for basic_indicator in basic_indicators:
            self.add_indicator(basic_indicator())

        # Advanced indicators
        adv_indicators = [
            UserTotalTasksCount, UserManagedTasksCount,
            UserLostTasksCount, UserMaxRingingDuration,
            UserAverageRingingDuration, UserMaxContactDuration,
            UserAverageContactDuration, UserTransferredTasks,
            UserMaxHoldDuration, UserVocalTotalOutboundDuration,
            UserAverageHoldDuration, UserVocalTotalWithdrawalDuration,
            UserProfileName, UserDisplayName, UserVocalMode,
            SessionLastLoginDate, UserCurrentTaskManagedDate,
            UserVocalState, VocalSessionId, IsLogged,
            RecordEnabled, VocalInterface, UserVocalPosition,
            UserCurrentTaskStartDate, StateStartTime, UserVocalStateStartDate,
            UserLogin, UserRawVocalState, SessionCurrentSpies,
        ]

        for adv_indicator in adv_indicators:
            self.add_indicator(adv_indicator(self.indicators))

        # Dailies indicators
        self.add_indicator(UserTotalLegCount(self.indicators, self.indicator_lut))  # NOQA
        self.add_indicator(UserContactedLegCount(self.indicators, self.indicator_lut))  # NOQA
        self.add_indicator(UserFailedLegCount(self.indicators, self.indicator_lut)) # NOQA
        self.add_indicator(UserCanceledLegCount(self.indicators, self.indicator_lut))   # NOQA
        self.add_indicator(UserOutboundContactTotalDuration(self.indicators, self.indicator_lut))   # NOQA
        self.add_indicator(UserOutboundContactMaxDuration(self.indicators, self.indicator_lut)) # NOQA
        self.add_indicator(UserOutboundContactAverageDuration(self.indicators, self.indicator_lut)) # NOQA

        # These three indicators are observed by external subscriptions

        # Observed by the RecordSubscription, dedicated to Records,
        # linked to record events writing on api server, through the middleware
        self.indicators['record_indicator'] = RecordIndicator(self.indicators)

        # Observed by the AutoRecordSubscription,
        # dedicated to Auto records functionality on middleware server.
        self.indicators['autorecord_session_watcher'] = \
            AutoRecordSessionWatcher(self.indicators)

        # Observed by the HistorySubscription, dedicated to History,
        # linked to history events writing on api server, through the middleware # NOQA
        self.indicators['user_activity'] = UserActivity(self.indicators, self.indicator_lut) # NOQA

    def get(self):
        return self.values

    def get_values(self, indicators_filtered=[], is_api=False):
        values = {'login': self.name} if not is_api else {}
        for indicator in self.indicators:
            if indicator in self.listenable_indicators or is_api:
                if indicators_filtered:
                    if indicator in indicators_filtered:
                        values.update(self.indicators[indicator].get())

                else:
                    values.update(self.indicators[indicator].get())

        return values

    def update(self, subject):
        self.values.update(subject.get())
        if not self.deferredCall:
            self.deferredCall = reactor.callLater(
                0.1,
                self.delayedNotification
            )

    def delayedNotification(self):
        self.notify()
        self.values = {'login': self.name}
        self.deferredCall = None

    def update_listenable_indicators(self, indicators):
        self.listenable_indicators = indicators

    def apply_data_for_withdrawal_states(self, data):
        for indicator_name in data:
            if indicator_name.startswith('user.state_pause'):
                if indicator_name not in self.indicators:
                    withdrawal_indicator = \
                        UserVocalTotalNamedWithdrawalDuration(
                            indicator_name
                        )
                    self.add_indicator(
                        withdrawal_indicator.totalNamedWithdrawalDuration
                    )
                    self.add_indicator(
                        withdrawal_indicator
                    )

                self.indicators[indicator_name].set(data[indicator_name])

    def get_withdrawal_indicator(self, indicator):
        pause_name = indicator[17:-20]
        withdrawal_indicator = UserVocalTotalNamedWithdrawalDuration(
            "user.state_pause_%s.duration('0')" % (pause_name,)
        )
        self.add_indicator(withdrawal_indicator.totalNamedWithdrawalDuration)
        self.add_indicator(withdrawal_indicator)

        return withdrawal_indicator


class Service(Subscribable):
    def __init__(self, name):
        super(Service, self).__init__()
        self.name = name
        self.subjects = []

        # Basic indicators

        basic_indicators = [
            LatentSessionsCount, LoggedSessionsCount,
            WorkingSessionsCount, RunningTasksCount,
            ContactDurationCount, WaitingDurationCount, ManagedTasksCountBasic,
            FailedTasksCount, MaxWaitingTimeThresholdCount,
            MaxEstimatedWaitingTimeThresholdCount,
            NotManageableWithLatentUsersCount,
            NotManageableWithoutLatentUsersCount, QueueName,
            MaxCurrentDurationContactTasksBasic, SupervisionSessionsCount,
            MaxDurationContactTasksBasic, MaxCurrentDurationWaitingTasksBasic,
            MaxDurationWaitingTasksBasic, QueueTechnicalName,
            WithdrawnSessionsCount, OutboundSessionsCount,
        ]

        for basic_indicator in basic_indicators:
            self.add_indicator(basic_indicator())

        # Advanced indicators

        adv_indicators = [
            UsersCount, AvailableUsersCount, ManagingUsersCount,
            CurrentTasksCount, WaitingTasksCount, AverageContactDuration,
            AverageWaitingDuration, NotManageableTasksCount,
            CanceledTasksCount, ManagedTasksRate, ServiceDisplayName,
            ManagedTasksCount, TotalTasksCount, MaxCurrentDurationContactTasks,
            MaxDurationContactTasks, MaxCurrentDurationWaitingTasks,
            MaxDurationWaitingTasks, WithdrawnUsersCount,
            OutboundUsersCount, SupervisionUsersCount,
        ]

        for adv_indicator in adv_indicators:
            self.add_indicator(adv_indicator(self.indicators))

    def update(self, subject):
        self.notify()

    def get_table_name(self):
        values = {
            self.indicators['name'].get(): self.indicators[
                'display_name'].get()
        }

        return values
