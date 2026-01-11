#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from ivcommons.dictionaries import InstanciatorDictionary
from ivcommons.log import Log

from cccp.protocols.errors import AvailabilityException
from cccp.protocols.rt.commlistener import CommunicationListener
from cccp.protocols.rt.dailylistener import DailyListener
from cccp.protocols.rt.subscription import Profile, Service

log = Log('cccp.protocols.rt.lookup')


class IndicatorLuT(object):

    def __init__(self):
        self.profiles = {}
        self.services = InstanciatorDictionary(Service)
        self.communications = {}
        self.communication_listener = CommunicationListener()
        self.daily_listener = DailyListener()

        self.autorecord_subscription = False
        self.record_subscription = False
        self.history_subscription = False

    def get_availability_from_login(self, login):
        for profile in self.profiles.values():
            for session in profile.sessions.values():
                if session.name == login:
                    if not session.indicators['is_logged'].value:
                        raise AvailabilityException('error.user_not_found')

                    return (
                        "available" if
                        session.indicators['user_vocal_state'].value in (
                            "available", "supervision")
                        else "unavailable"
                    )

        raise AvailabilityException('error.user_not_found')

    def get_communication_listener(self):
        return self.communication_listener

    def get_daily_listener(self):
        return self.daily_listener

    def get_queues_table(self):
        table = {}
        for name in self.services:
            table.update(self.services[name].get_table_name())

        return table

    def get_values_from_profiles(self, indicators, ignored_profiles=[]):
        result = []
        for profile in self.profiles.values():
            if profile.name in ignored_profiles:
                continue

            _results = profile.get_values('session', indicators, is_api=True)
            for row in _results:
                result.append(self._filter_results(row))

        return result

    def _filter_results(self, row):
        data = {}
        for indicator in row:
            data[indicator] = {'value': row[indicator]['value']}

        return data

    def add_profile(self, name):
        self.profiles[name] = Profile(name, self)
        return self.profiles[name]

    def del_profile(self, name):
        del self.profiles[name]

    def has_profile(self, name):
        return name in self.profiles

    def get_profile(self, name):
        return self.profiles[name]

    def add_service(self, name):
        self.services[name] = Service(name)
        return self.services[name]

    def del_service(self, name):
        del self.services[name]

    def has_service(self, name):
        return name in self.services

    def get_service(self, name):
        return self.services[name]

    def get_consistent_session_id(self):
        if "Superviseur_default" in self.profiles:
            session = self.get_profile("Superviseur_default").get_session(
                'consistent')
            return session.get_values(['vocal_session_id'], is_api=True).get(
                'vocal_session_id', {'value': {}}).get('value')
        return None

    def set_record_indicators(self, record_subscription):
        if not self.record_subscription:
            self.record_subscription = record_subscription

        _indicators = []
        for profile_name in self.profiles:
            profile = self.get_profile(profile_name)

            for session_name in profile.sessions:
                session = profile.get_session(session_name)
                _indicators.append(session.get_indicator("record_indicator"))

        self.record_subscription.add_subjects(_indicators)

        self.record_subscription.add_subject(self.communication_listener)

    def update_record_subscription(self, record_indicator):
        if self.record_subscription:
            self.record_subscription.add_subjects([record_indicator])

    def set_history_indicators(self, history_subscription):
        if not self.history_subscription:
            self.history_subscription = history_subscription

        _indicators = []
        for profile_name in self.profiles:
            profile = self.get_profile(profile_name)

            for session_name in profile.sessions:
                session = profile.get_session(session_name)
                _indicators.append(session.get_indicator("user_activity"))

        self.history_subscription.add_subjects(_indicators)

    def update_history_subscription(self, history_indicator):
        if self.history_subscription:
            self.history_subscription.add_subjects([history_indicator])

    def set_autorecord_session_watchers(self, autorecord_subscription):
        if not self.autorecord_subscription:
            self.autorecord_subscription = autorecord_subscription

        _indicators = []
        for profile_name in self.profiles:
            profile = self.get_profile(profile_name)

            for session_name in profile.sessions:
                session = profile.get_session(session_name)
                _indicators.append(
                    session.get_indicator("autorecord_session_watcher")
                )

        self.autorecord_subscription.add_subjects(_indicators)
        # Allow to retrieve data for current users
        for _indicator in _indicators:
            self.autorecord_subscription.update(_indicator)

    def update_autorecord_subscription(self, autorecord_session_watcher):
        if self.autorecord_subscription:
            self.autorecord_subscription.add_subjects(
                [autorecord_session_watcher]
            )

    def get_indicators(self, target_name, type, profile_name, indicators=[]):
        _indicators = []
        if type == "service":
            service = self.get_service(target_name)

            for indicator in indicators:
                if service.has_indicator(indicator):
                    _indicators.append(service.get_indicator(indicator))

                else:
                    raise LookupError(
                        "Unknown indicator name '%s'" % (
                            indicator
                        )
                    )

        elif type == "session":
            if profile_name:
                if not self.has_profile(profile_name):
                    profile = self.add_profile(profile_name)

                else:
                    profile = self.get_profile(profile_name)

                session = profile.get_session(target_name)

                for indicator in indicators:
                    if session.has_indicator(indicator):
                        _indicators.append(session.get_indicator(indicator))

                    elif indicator.startswith('user_vocal_total_named') and \
                            indicator.endswith('withdrawal_duration'):
                        _indicators.append(
                            session.get_withdrawal_indicator(
                                indicator
                            )
                        )

                    else:
                        raise LookupError(
                            "Unknown indicator name '%s'" % (
                                indicator
                            )
                        )

            else:
                raise LookupError(
                    "Profile_name is missing, impossible to subscribe "
                    "to a session's indicator."
                )

        else:
            raise LookupError(
                "Invalid type [%s] provided." % (
                    type,
                )
            )
        return _indicators

    def add_profile_indicators(self, target, _type, indicators_list):
        if not self.has_profile(target):
            profile = self.add_profile(target)

        else:
            profile = self.get_profile(target)

        for indicator in indicators_list:
            if not profile.has_indicator(indicator, _type):
                profile.add_indicator(indicator, _type)

        return profile

    def del_profile_indicators(self, target, _type, indicators_list):
        if not self.has_profile(target):
            profile = self.add_profile(target)

        else:
            profile = self.get_profile(target)

        for indicator in indicators_list:
            if profile.has_indicator(indicator, _type):
                profile.del_indicator(indicator, _type)

        return profile

    def reset(self, log=log):
        log.system_message(
            'CCCP - Resetting values for %d services and %d profiles.' % (
                len(self.services), len(self.profiles)
            )
        )
        for service in self.services.values():
            service.reset()

        for profile in self.profiles.values():
            profile.reset(log=log)
