#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import json

from datetime import datetime

try:
    from itertools import izip
except ImportError:
    izip = zip

from cccp.protocols.converter import Converter
from cccp.protocols.commons import IncrementIdReservation
from cccp.protocols.rt.lookup import IndicatorLuT
from cccp.protocols.rt.subscriber import Subscriber

from ivcommons.log import Log
from ivcommons.time import seconds_delta_from_future_time

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from collections import defaultdict

log = Log("cccp.protocols.dispatch")


class BaseDispatchClient(object):
    interval = 86400

    def __init__(self, reset_time, is_callflow):
        """
        This class contains the "core" of the Dispatch client.
        Must be inherited with a sync or async client to be able to
        communicate with a real Dispatch.

        :param ip: IP or hostname of Dispatch server.
        :type ip: str
        :param port: Port of Dispatch server
        :type port: int
        """
        self.converter = Converter()
        self._service_xqueries_list = sorted(
            [
                "name",
                "display_name",
                "latent_sessions_count",
                "logged_sessions_count",
                "working_sessions_count",
                "withdrawn_sessions_count",
                "outbound_sessions_count",
                "supervision_sessions_count",
                "running_tasks_count",
                "waiting_tasks_count",
                "contact_duration.count('0')",
                "waiting_duration.count('0')",
                "max_waiting_time_threshold.count('0')",
                "max_estimated_waiting_time_threshold.count('0')",
                "not_manageable_with_latent_users.count('0')",
                "not_manageable_without_latent_users.count('0')",
                "managed_tasks.count('0')",
                "failed_tasks.count('0')",
                "oldest_contact_date",
                "contact_duration.max('0')",
                "oldest_waiting_date",
                "waiting_duration.max('0')",
            ]
        )

        self._user_xqueries_list = sorted(
            [
                "login",
                "name",
                "contact_duration.max('0')",
                "hold_duration.max('0')",
                "ringing_duration.max('0')",
                "state_group_pause.duration('0')",
                "state_group_outbound.duration('0')",
                "states.last.state.start_date",
                "last_state_display_name",
                "last_state_name",
                "last_state_date",
                "last_task_display_name",
                "last_task_name",
                "tasks.last.task.start_date",
                "tasks.last.task.management_effective_date",
                "tasks.last.task.end_date",
                "total_inbound.count('0')",
                "lost_inbound.count('0')",
                "managed_inbound.count('0')",
                "total_tasks.count('0')",
                "transferred_inbound.count('0')",
                "redirected_inbound.count('0')",
                "task_state_held.duration('0')",
                "task_state_ringing.duration('0')",
                "task_state_contact.duration('0')",
                "sessions.last.session.login_date",
                "sessions.last.session.logout_date",
                "sessions.last.session.profile_name",
                "sessions.last.session.session_id",
                "sessions.last.session.last_record.value",
                "sessions.last.session.record_active.value",
                "sessions.last.session.current_spies.value",
                "sessions.last.session.current_mode",
                "sessions.last.session.phone_uri",
                "sessions.last.session.logged",
                "busy_count",
            ]
        )

        self._user_xqueries_list_callflow = sorted(
            [
                "login",
                "name",
                "sessions.last.session.session_id",
                "sessions.last.session.profile_name",
                "sessions.last.session.logged",
                "sessions.last.session.last_record.value",
                "sessions.last.session.record_active.value",
            ]
        )

        self._withdrawal_xqueries_list = sorted(["user.login", "profile_name"])

        self._communication_session_xqueries_list = sorted(
            [
                "create_date",
                "session_type",
                "session_id",
                "terminate_date",
                "user.login",
                "user.name",
                "manager_session.user.login",
                "manager_session.profile_name",
                "queue_name",
                "attributes.local_number.value",
                "attributes.remote_number.value",
                "start_date",
                "management_effective_date",
                "last_record.value",
                "record_active.value",
            ]
        )

        self._communication_session_xqueries_list_callflow = sorted(
            ["session_id", "terminate_date", "last_record.value", "record_active.value"]
        )

        self._outbound_communication_session_xqueries_list = sorted(
            [
                "user.login",
                "user.name",
                "profile_name",
                "session_id",
                "outbound_call_id.value",
                "outbound_state.value",
                "outbound_hold_flag.value",
                "last_outbound_call_start.value",
                "last_outbound_call_contact_start.value",
                "last_outbound_call_target.value",
                "total_leg_count.value",
                "contacted_leg_count.value",
                "failed_leg_count.value",
                "canceled_leg_count.value",
                "outbound_contact_duration.value",
                "outbound_max_contact_duration.value",
                "last_outgoing_activity.value",
                "last_transfer_activity.value",
            ]
        )

        self._outbound_daily_communication_session_xqueries_list = sorted(
            [
                "user.login",
                "profile_name",
                "session_id",
                "total_leg_count.value",
                "contacted_leg_count.value",
                "failed_leg_count.value",
                "canceled_leg_count.value",
                "outbound_contact_duration.value",
                "outbound_max_contact_duration.value",
            ]
        )

        self._communication_queue_xqueries_list = sorted(
            [
                "attributes.local_number.value",
                "attributes.remote_number.value",
                "session.session_id",
                "queue_name",
            ]
        )

        self._communication_task_xqueries_list = sorted(
            [
                "task_id",
                "parent_call_session_id",
                "manager_session.profile_name",
                "start_date",
                "end_date",
                "stop_waiting_date",
                "management_date",
                "post_management_date",
                "queue_type",  # user or queue
                "queue_display_name",
                "manager_session.user.login",
            ]
        )

        self.next_format_id = IncrementIdReservation()
        self.next_idx = IncrementIdReservation()
        self.service_done = False
        self.tables = {}
        self.queues = defaultdict(list)
        self.service_data = {}
        self.indicator_lut = IndicatorLuT()
        self.subscriber = Subscriber(self.indicator_lut)
        self.queue_view_idx = None
        self.user_view_idx = None
        self.withdrawal_view_idx = None
        self.communication_session_view_idx = None
        self.communication_queue_view_idx = None
        self.communication_task_view_idx = None
        self.outbound_communication_session_view_idx = None
        self.outbound_daily_communication_session_view_idx = None
        self.xqueries_tables = {}

        self.reset_loop = None

        if reset_time is not None:
            self._setup_reset(reset_time, is_callflow)

        self.deferredClean = None
        self.pending_communications = []
        self.auxiliary_pending_communications = []
        self.is_callflow = is_callflow

    def _replace_profiles(self, profiles):
        # Not used, for the beauty.
        return map(lambda x: x.replace(" ", "_"), profiles)

    def _reset(self, auto=True, log=log):
        self.subscriber.reset(log=log)
        self.indicator_lut.get_daily_listener().reset()

        if not self.is_callflow:
            if self.queue_view_idx:
                self.stop_view(self.queue_view_idx)
                self.queue_view_idx = self.start_view(
                    "queues",
                    "queues",
                    self._service_xqueries_list,
                    ".[virtual_queue eq 0 and running]",
                )

            if self.user_view_idx:
                self.stop_view(self.user_view_idx)
                self.user_view_idx = self.start_view(
                    "users",
                    "users",
                    self._user_xqueries_list,
                    ".[sessions/last/session/profile_name "
                    "ne 'Superviseur_default' and group/path eq '/default' "
                    "or login eq 'consistent']",
                )

            if self.withdrawal_view_idx:
                self.stop_view(self.withdrawal_view_idx)
                self.withdrawal_view_idx = self.start_view(
                    "sessions",
                    "users_sessions",
                    self._withdrawal_xqueries_list,
                    ".[session_type eq 3 and terminate_date eq '' and "
                    "profile_name ne 'Superviseur_default']",
                )

            if self.communication_session_view_idx:
                self.stop_view(self.communication_session_view_idx)
                self.communication_session_view_idx = self.start_view(
                    "sessions",
                    "communications_sessions",
                    self._communication_session_xqueries_list,
                    ".[connections/last/call_id ne '' and session_type ne 3]",
                )

            if self.outbound_daily_communication_session_view_idx:
                self.stop_view(self.outbound_daily_communication_session_view_idx)
                if auto:
                    self.current_daily_outbound_xquery_filters = (
                        ".[session_type eq 3 and terminate_date gt '%s' "
                        "and profile_name ne 'Superviseur_default' "
                        "and user/group/path eq '/default']"
                        % datetime.now().strftime(  # NOQA
                            "%Y/%m/%d %H:%M:%S"
                        )
                    )

                self.outbound_daily_communication_session_view_idx = self.start_view(  # NOQA
                    "sessions",
                    "outbound_communications_sessions",
                    self._outbound_daily_communication_session_xqueries_list,
                    self.current_daily_outbound_xquery_filters,
                )

            if self.outbound_communication_session_view_idx:
                self.stop_view(self.outbound_communication_session_view_idx)
                self.outbound_communication_session_view_idx = self.start_view(
                    "sessions",
                    "outbound_communications_sessions",
                    self._outbound_communication_session_xqueries_list,
                    ".[session_type eq 3 and terminate_date eq '' "
                    "and profile_name ne 'Superviseur_default' "
                    "and user/group/path eq '/default']",
                )

            if self.communication_queue_view_idx:
                self.stop_view(self.communication_queue_view_idx)
                self.communication_queue_view_idx = self.start_view(
                    "file_tasks",
                    "communications_queues",
                    self._communication_queue_xqueries_list,
                    ".[terminate_date eq '']",
                )

            if self.communication_task_view_idx:
                self.stop_view(self.communication_task_view_idx)
                self.communication_task_view_idx = self.start_view(
                    "tasks",
                    "communications_tasks",
                    self._communication_task_xqueries_list,
                    "",
                )
        else:
            if self.user_view_idx:
                self.stop_view(self.user_view_idx)
                self.user_view_idx = self.start_view(
                    "users",
                    "users",
                    self._user_xqueries_list_callflow,
                    ".[sessions/last/session/profile_name "
                    "ne 'Superviseur_default' and group/path eq '/default' "
                    "or login eq 'consistent']",
                )
            if self.communication_session_view_idx:
                self.stop_view(self.communication_session_view_idx)
                self.communication_session_view_idx = self.start_view(
                    "sessions",
                    "communications_sessions",
                    self._communication_session_xqueries_list_callflow,
                    ".[connections/last/call_id ne '' and session_type ne 3]",
                )

    def _start_reset_loop(self):
        """
        Start the reset loop that resets the counters on a daily basis. This
        function assumes uses `self.interval` as the call rythm.

        `LoopingCall` automatically fires when we start it, so there is no need
        to call `_reset` separately.
        """
        log.system_message(
            "Setting up counters reset every %d seconds (%d hours)."
            % (self.interval, self.interval / 3600)
        )
        self.reset_loop.start(self.interval)

    def _setup_reset(self, reset_time, is_callflow):
        """
        Setup the stuff we need to have a looping call that resets the counters
        on a daily basis. This function calculates the number of seconds left
        until the next `reset_time`. It then asks the reactor to call
        `_start_reset_loop` to initiate the reset loop.

        :param reset_time: An ISO 8601 string describing the time at which the
            reset should occur.
        """
        self.reset_loop = LoopingCall(self._reset)
        seconds_left = seconds_delta_from_future_time(reset_time)
        log.system_message(
            "Programming initial counters reset in %d seconds (%s)."
            % (seconds_left, reset_time)
        )

        reactor.callLater(seconds_left, self._start_reset_loop)

    def get_availability_from_login(self, login):
        return self.indicator_lut.get_availability_from_login(login)

    def set_withdrawal_view(self, withdrawal_list):
        list_changed = False

        for withdrawal_name in withdrawal_list:
            if (
                "user.state_%s.duration('0')" % (withdrawal_name)
                not in self._withdrawal_xqueries_list
            ):
                self._withdrawal_xqueries_list.append(
                    "user.state_%s.duration('0')" % (withdrawal_name)
                )
                list_changed = True

        if not list_changed:
            return

        self._withdrawal_xqueries_list.sort()

        if self.withdrawal_view_idx:
            self.stop_view(self.withdrawal_view_idx)

        self.withdrawal_view_idx = self.start_view(
            "sessions",
            "users_sessions",
            self._withdrawal_xqueries_list,
            ".[session_type eq 3 and terminate_date eq '' and "
            "profile_name ne 'Superviseur_default']",
        )

    def start_view(self, db_root, _type, xqueries_list="", _filter=""):
        format_id = self.set_format(xqueries_list, db_root, _type)
        defaults = self.compute_defaults(xqueries_list)
        idx = self.next_idx.reserve()
        log.debug(
            "Dispatch view started on %s with idx %s."
            % (
                str(db_root),
                str(idx),
            )
        )
        view = {}
        self.tables[idx] = (view, format_id, defaults, [])

        reactor.callLater(0.2, self.query_list, idx, db_root, _filter)

        log.debug(
            "Dispatch list query started on %s with idx %s."
            % (
                str(db_root),
                str(idx),
            )
        )
        return idx

    def stop_view(self, idx):
        if idx not in self.tables:
            log.debug(
                "The view with idx %s seems to have been already stopped." % (str(idx),)
            )
            return
        _, format_id, _, ids = self.tables[idx]

        for i in ids:
            log.debug("Dispatch query stopped with idx %s." % (str(i),))
            self.stop_query(i)
            # We don't release i because we don't want to retrieve the same
            # values when starting a same view with the same i
            # self.next_idx.release(i)

        self.stop_query(idx)
        log.debug("Dispatch query stopped with idx %s." % (str(idx),))
        del self.tables[idx]
        # We don't release i because we don't want to retrieve the same values
        # when starting a same view with the same i
        # self.next_idx.release(idx)
        # self.next_format_id.release(format_id)

    def on_list_response(self, session_id, idx, object):
        if idx not in self.tables:
            log.debug(
                "Dispatch list response about an unknown view with idx %s."
                % (str(idx),)
            )
            self.stop_query(idx)
            return

        view, format_id, defaults, ids = self.tables[idx]
        for item in object.items:
            obj_id = item.item_id
            if item.action == 2:
                if obj_id in view:
                    log.debug("Dispatch object %s deleted." % (str(obj_id),))
                    del view[obj_id]
                    return

                else:
                    log.debug(
                        "Dispatch delete request on an object not in the "
                        "list with idx %s !" % (str(idx),)
                    )

            if obj_id not in view:
                view[obj_id] = list(defaults)

            if format_id > 0:
                i = self.next_idx.reserve()
                ids.append(i)
                self.query_object(idx, obj_id, format_id, obj_id)
                log.debug(
                    "Dispatch object query started on id %s with idx %s."
                    % (
                        str(obj_id),
                        str(i),
                    )
                )

    def on_object_response(self, session_id, idx, object, obj_id):
        try:
            if idx not in self.tables:
                log.debug(
                    "Dispatch details about an object in an unknown view "
                    "with idx %s." % (str(idx),)
                )
                self.stop_query(idx)
                return

            view, _, defaults, _ = self.tables[idx]
            if obj_id not in view:
                log.debug(
                    "Dispatch details about an object not in the list with "
                    "idx %s! Object %s added."
                    % (
                        str(idx),
                        str(obj_id),
                    )
                )
                view[obj_id] = list(defaults)

            for e in object.values:
                if hasattr(e, "value"):
                    if idx == self.withdrawal_view_idx:
                        index = self._withdrawal_xqueries_list.index(
                            self.xqueries_tables["users_sessions"][e.field_index]
                        )
                        view[obj_id][index] = e.value

                    elif idx == self.communication_session_view_idx:
                        if not self.is_callflow:
                            index = self._communication_session_xqueries_list.index(
                                self.xqueries_tables["communications_sessions"][
                                    e.field_index
                                ]
                            )
                            view[obj_id][index] = e.value
                        else:
                            index = self._communication_session_xqueries_list_callflow.index(
                                self.xqueries_tables["communications_sessions"][
                                    e.field_index
                                ]
                            )
                            view[obj_id][index] = e.value

                    elif idx == self.outbound_communication_session_view_idx:
                        index = (
                            self._outbound_communication_session_xqueries_list.index(  # NOQA
                                self.xqueries_tables[
                                    "outbound_communications_sessions"
                                ][e.field_index]
                            )
                        )
                        view[obj_id][index] = e.value

                    elif idx == self.outbound_daily_communication_session_view_idx:  # NOQA
                        index = self._outbound_daily_communication_session_xqueries_list.index(  # NOQA
                            self.xqueries_tables[
                                "outbound_daily_communications_sessions"
                            ][e.field_index]
                        )
                        view[obj_id][index] = e.value

                    elif idx == self.communication_queue_view_idx:
                        index = self._communication_queue_xqueries_list.index(
                            self.xqueries_tables["communications_queues"][e.field_index]
                        )
                        view[obj_id][index] = e.value

                    elif idx == self.communication_task_view_idx:
                        index = self._communication_task_xqueries_list.index(
                            self.xqueries_tables["communications_tasks"][e.field_index]
                        )
                        view[obj_id][index] = e.value

                    elif idx == self.queue_view_idx:
                        index = self._service_xqueries_list.index(
                            self.xqueries_tables["queues"][e.field_index]
                        )
                        view[obj_id][index] = e.value

                    elif idx == self.user_view_idx:
                        if not self.is_callflow:
                            index = self._user_xqueries_list.index(
                                self.xqueries_tables["users"][e.field_index]
                            )
                            view[obj_id][index] = e.value
                        else:
                            index = self._user_xqueries_list_callflow.index(
                                self.xqueries_tables["users"][e.field_index]
                            )
                            view[obj_id][index] = e.value

                else:
                    if idx == self.withdrawal_view_idx:
                        index = self._withdrawal_xqueries_list.index(
                            self.xqueries_tables["users_sessions"][e.field_index]
                        )
                        view[obj_id][index] = None

                    elif idx == self.communication_session_view_idx:
                        if not self.is_callflow:
                            index = self._communication_session_xqueries_list.index(
                                self.xqueries_tables["communications_sessions"][
                                    e.field_index
                                ]
                            )
                            view[obj_id][index] = None
                        else:
                            index = self._communication_session_xqueries_list_callflow.index(
                                self.xqueries_tables["communications_sessions"][
                                    e.field_index
                                ]
                            )
                            view[obj_id][index] = None

                    elif idx == self.outbound_communication_session_view_idx:
                        index = (
                            self._outbound_communication_session_xqueries_list.index(  # NOQA
                                self.xqueries_tables[
                                    "outbound_communications_sessions"
                                ][e.field_index]
                            )
                        )
                        view[obj_id][index] = None

                    elif idx == self.outbound_daily_communication_session_view_idx:  # NOQA
                        index = self._outbound_daily_communication_session_xqueries_list.index(  # NOQA
                            self.xqueries_tables[
                                "outbound_daily_communications_sessions"
                            ][e.field_index]
                        )
                        view[obj_id][index] = None

                    elif idx == self.communication_queue_view_idx:
                        index = self._communication_queue_xqueries_list.index(
                            self.xqueries_tables["communications_queues"][e.field_index]
                        )
                        view[obj_id][index] = None

                    elif idx == self.communication_task_view_idx:
                        index = self._communication_task_xqueries_list.index(
                            self.xqueries_tables["communications_tasks"][e.field_index]
                        )
                        view[obj_id][index] = None

                    elif idx == self.queue_view_idx:
                        index = self._service_xqueries_list.index(
                            self.xqueries_tables["queues"][e.field_index]
                        )
                        view[obj_id][index] = None

                    elif idx == self.user_view_idx:
                        if not self.is_callflow:
                            index = self._user_xqueries_list.index(
                                self.xqueries_tables["users"][e.field_index]
                            )
                            view[obj_id][index] = None
                        else:
                            index = self._user_xqueries_list_callflow.index(
                                self.xqueries_tables["users"][e.field_index]
                            )
                            view[obj_id][index] = None

            if idx == self.withdrawal_view_idx:
                data = dict(izip(self._withdrawal_xqueries_list, view[obj_id]))
                self.on_withdrawal_update(data)

            elif idx == self.queue_view_idx:
                data = dict(izip(self._service_xqueries_list, view[obj_id]))
                self.on_service_update(data)

            elif idx == self.user_view_idx:
                if not self.is_callflow:
                    data = dict(izip(self._user_xqueries_list, view[obj_id]))
                    self.on_user_update(data, view[obj_id])
                else:
                    data = dict(izip(self._user_xqueries_list_callflow, view[obj_id]))
                    self.on_user_update(data, view[obj_id])

            elif idx == self.communication_session_view_idx:
                if not self.is_callflow:
                    data = dict(
                        izip(self._communication_session_xqueries_list, view[obj_id])
                    )
                    self.on_communication_session_update(data)
                else:
                    data = dict(
                        izip(
                            self._communication_session_xqueries_list_callflow,
                            view[obj_id],
                        )
                    )
                    self.on_communication_session_update(data)

            elif idx == self.outbound_communication_session_view_idx:
                data = dict(
                    izip(
                        self._outbound_communication_session_xqueries_list, view[obj_id]
                    )
                )
                self.on_outbound_communication_session_update(data)

            elif idx == self.outbound_daily_communication_session_view_idx:
                data = dict(
                    izip(
                        self._outbound_daily_communication_session_xqueries_list,
                        view[obj_id],
                    )
                )
                self.on_outbound_daily_communication_session_update(data)

            elif idx == self.communication_queue_view_idx:
                data = dict(izip(self._communication_queue_xqueries_list, view[obj_id]))
                self.on_communication_queue_update(data)

            elif idx == self.communication_task_view_idx:
                data = dict(izip(self._communication_task_xqueries_list, view[obj_id]))
                self.on_communication_task_update(data)

            elif len(view[obj_id]) == 2:
                self.on_service_list(view[obj_id])

        except Exception as e:
            log.exception()

    def on_service_list(self, object):
        user = object[1]
        if object[0] != "":
            active_queues = json.loads(object[0])
            for queue in active_queues:
                if active_queues[queue]["type"] == "queue":
                    if active_queues[queue]["queue"] in self.queues:
                        self.queues[active_queues[queue]["queue"]].append(user)
                    else:
                        self.queues[active_queues[queue]["queue"]] = [user]

            queues_dict = {}
            for queue in active_queues:
                if active_queues[queue]["queue"] in self.service_data:
                    data = {}
                    for i in range(len(self._service_xqueries_list)):
                        data[self._service_xqueries_list[i]] = self.service_data[
                            active_queues[queue]["queue"]
                        ][i]
                    queues_dict.update({data["name"]: data["display_name"]})

            self.on_add_queues(user, queues_dict)

            for queue in active_queues:
                if active_queues[queue]["queue"] in self.service_data:
                    data = {}
                    for i in range(len(self._service_xqueries_listt)):
                        data[self._service_xqueries_list[i]] = self.service_data[
                            active_queues[queue]["queue"]
                        ][i]
                    self.view_change(user, active_queues[queue]["queue"], data)
        else:
            for queue in self.queues:
                if user in self.queues[queue]:
                    if queue in self.service_data:
                        data = {}
                        for i in range(len(self._service_xqueries_listformat)):
                            data[self._service_xqueries_list[i]] = self.service_data[
                                queue
                            ][i]
                        self.view_change(user, queue, data)

    def on_withdrawal_update(self, data):
        if not self.indicator_lut.has_profile(data["profile_name"]):
            profile = self.indicator_lut.add_profile(data["profile_name"])

        else:
            profile = self.indicator_lut.get_profile(data["profile_name"])

        session = profile.get_session(data["user.login"])
        session.apply_data_for_withdrawal_states(data)

    def on_user_update(self, data, view_obj):
        # This method just do a get_session when receiving a update, in order
        # to populate sessions in a given profile
        if data["sessions.last.session.session_id"]:
            if not self.indicator_lut.has_profile(
                data["sessions.last.session.profile_name"]
            ):
                profile = self.indicator_lut.add_profile(
                    data["sessions.last.session.profile_name"]
                )

            else:
                profile = self.indicator_lut.get_profile(
                    data["sessions.last.session.profile_name"]
                )

            if "name" in data:
                data["user.name"] = data["name"]

            session = profile.get_session(data["login"])
            session.apply_data(data)

        if not data["sessions.last.session.logged"]:
            if not self.is_callflow:
                view_obj[
                    self._user_xqueries_list.index("sessions.last.session.session_id")
                ] = None
            else:
                view_obj[
                    self._user_xqueries_list_callflow.index(
                        "sessions.last.session.session_id"
                    )
                ] = None

    def on_communication_session_update(self, data):
        clistener = self.indicator_lut.get_communication_listener()
        communication_id = data["session_id"]
        if "last_record.value" in data:
            data["sessions.last.session.last_record.value"] = data.pop(
                "last_record.value"
            )

        if "record_active.value" in data:
            data["sessions.last.session.record_active.value"] = data.pop(
                "record_active.value"
            )

        if not clistener.has_communication(communication_id):
            clistener.add_communication(communication_id)

        _communication = clistener.get_communication(communication_id)
        _communication.apply_data(data)

        if data.get("terminate_date"):
            self.clean_communication(communication_id)

    def on_outbound_communication_session_update(self, data):
        if data["user.login"] and data["profile_name"]:
            if not self.indicator_lut.has_profile(data["profile_name"]):
                session = self.indicator_lut.add_profile(
                    data["profile_name"]
                ).get_session(data["user.login"])

            else:
                session = self.indicator_lut.get_profile(
                    data["profile_name"]
                ).get_session(data["user.login"])

            session.apply_data(data)

            if data["outbound_call_id.value"]:
                # Tricks for communication.apply_data
                data["queue_type"] = "outbound"
                data["manager_session.profile_name"] = data["profile_name"]

                # Remove initial/current agent/queue name
                # data['queue_display_name'] = data['user.login']
                # data['manager_session.user.login'] = data['user.login']

                data["create_date"] = data["last_outbound_call_start.value"]
                data["communication_create_date"] = {
                    "value": data["last_outbound_call_start.value"]
                }
                data["attributes.local_number.value"] = data[
                    "last_outbound_call_target.value"
                ]
                data["attributes.remote_number.value"] = data["user.name"]

                # Tricks for clistener.apply_task_data
                data["task_id"] = data["outbound_call_id.value"]
                data["parent_call_session_id"] = data["outbound_call_id.value"]
                # data['start_date'] = data['last_outbound_call_start.value']
                data["management_date"] = data["last_outbound_call_contact_start.value"]

                if data["last_outbound_call_start.value"] == "stop":
                    data["end_date"] = datetime.now().isoformat()
                else:
                    data["end_date"] = ""

                clistener = self.indicator_lut.get_communication_listener()
                communication_id = data["outbound_call_id.value"]

                if not clistener.has_communication(communication_id):
                    clistener.add_communication(
                        communication_id, communication_type="outbound"
                    )

                _communication = clistener.get_communication(communication_id)
                _communication.apply_data(data)
                clistener.apply_task_data(data)

    def on_outbound_daily_communication_session_update(self, data):
        if data["user.login"] and data["profile_name"] and data["session_id"]:
            daily_listener = self.indicator_lut.get_daily_listener()
            daily_listener.apply_data(
                data["profile_name"], data["user.login"], data["session_id"], data
            )

    def clean_communication(self, communication_id):
        if not self.deferredClean:
            self.pending_communications.append(communication_id)
            self.deferredClean = reactor.callLater(10, self._delayed_clean)

        else:
            self.auxiliary_pending_communications.append(communication_id)

    def _delayed_clean(self):
        clistener = self.indicator_lut.get_communication_listener()
        for communication_id in self.pending_communications:
            clistener.del_communication(communication_id)

        if self.auxiliary_pending_communications:
            self.pending_communications = list(self.auxiliary_pending_communications)
            self.auxiliary_pending_communications = []
            self.deferredClean = reactor.callLater(10, self._delayed_clean)

        else:
            self.pending_communications = []
            self.deferredClean = None

    def on_communication_queue_update(self, data):
        try:
            service = self.indicator_lut.get_service(data["queue_name"])
            service_name = service.get_table_name()[data["queue_name"]]

        except KeyError:
            log.error(
                "An Error occured, can't get update from file_task: %s" % (repr(data),)
            )

        else:
            data["queue_display_name"] = service_name
            data["queue_type"] = "queue"

            clistener = self.indicator_lut.get_communication_listener()
            communication_id = data["session.session_id"]

            if not clistener.has_communication(communication_id):
                clistener.add_communication(communication_id)

            _communication = clistener.get_communication(communication_id)
            _communication.apply_data(data)

    def on_communication_task_update(self, data):
        clistener = self.indicator_lut.get_communication_listener()
        clistener.apply_task_data(data)

    def get_values_from_profiles(self, indicators, ignored_profiles=[]):
        return self.indicator_lut.get_values_from_profiles(
            indicators, ignored_profiles=ignored_profiles
        )

    def subscribe(self, targets, type, indicators=[], profile_name=None, **kwargs):
        return self.subscriber.subscribe(
            targets, type, indicators, profile_name if profile_name else None
        )

    def subscribe_profile(self, target, indicators_list, whitelabel=None, project=None):
        return self.subscriber.subscribe_profile(target, "session", indicators_list)

    def unsubscribe_profile(self, subscription_id, data=[]):
        if data:
            return self.subscriber.update_profile_indicators(
                subscription_id, "session", removed_indicators=data
            )

        else:
            self.subscriber.unsubscribe(subscription_id)

    def subscribe_communication(
        self,
        target,
        indicators_list,
        profiles_list,
        queues_list,
        whitelabel=None,
        project=None,
    ):
        return self.subscriber.subscribe_communication(
            target, indicators_list, profiles_list, queues_list
        )

    def update_communication_subscription(
        self, subscription_id, indicators_list, profiles_list, queues_list
    ):
        return self.subscriber.update_communication_indicators(
            subscription_id,
            profiles_list=profiles_list,
            queues_list=queues_list,
            added_indicators=indicators_list,
        )

    def unsubscribe_communication(
        self, subscription_id, data=[], profiles_list=[], queues_list=[]
    ):
        if data and profiles_list and queues_list:
            return self.subscriber.update_communication_indicators(
                subscription_id, removed_indicators=data
            )

        else:
            self.subscriber.unsubscribe(subscription_id)

    def update_subscription(
        self, subscription_id, _type, indicators, subtype="session"
    ):
        if _type != "profile":
            return self.subscriber.update_subscription(subscription_id, indicators, [])

        else:
            return self.subscriber.update_profile_indicators(
                subscription_id, subtype, added_indicators=indicators
            )

    def unsubscribe(self, subscription_id, data=[]):
        if data:
            return self.subscriber.update_subscription(subscription_id, [], data)

        else:
            self.subscriber.unsubscribe(subscription_id)

    def on_service_update(self, data):
        service = self.indicator_lut.get_service(data["name"])
        service.apply_data(data)

    def compute_defaults(self, format):
        f = []
        for s in sorted(format):
            try:
                if s[-5:] == "count":
                    f.append(0)

                elif s[-5:] == "_date":
                    f.append(None)

                elif s[-8:] == "duration":
                    f.append(0)

                elif s[-13:] == "duration('0')":
                    f.append(0)

                elif s[-10:] == "count('0')":
                    f.append(0)

                else:
                    f.append("")

            except:
                f.append("")
        return f

    def set_format(self, xqueries_list, db_root, _type):
        if xqueries_list == "":
            return 0
        cst_object, xqueries_table = self.converter.create_cst_object(xqueries_list)
        self.xqueries_tables[_type] = xqueries_table
        cst_object.format_id = self.next_format_id.reserve()
        self.set_object_format(cst_object)
        return cst_object.format_id

    def get_users_list(self, profiles):
        user_list = []
        for profile_name in profiles:
            if self.indicator_lut.has_profile(profile_name):
                profile = self.indicator_lut.get_profile(profile_name)
                user_list.extend(profile.get_session_list())

        return user_list

    def get_communications_list(self, profiles_list, queues_list, **kwargs):
        clistener = self.indicator_lut.get_communication_listener()
        return clistener.get_communication_list(profiles_list, queues_list)

    def get_consistent_session_id(self):
        return self.indicator_lut.get_consistent_session_id()

    def on_add_queues(self, user, queue_names):
        log.debug("[%s] subscribed to the queues : %s" % (user, queue_names))

    def query_list(self, idx, db_root, filter):
        raise NotImplementedError()

    def query_object(self, idx, id, format_id, obj_id):
        raise NotImplementedError()

    def stop_query(self, idx):
        raise NotImplementedError()

    def set_object_format(self, cst_format):
        raise NotImplementedError()
