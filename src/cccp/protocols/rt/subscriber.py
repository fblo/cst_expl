#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from copy import deepcopy

from ivcommons.hash import compute_key
from ivcommons.log import Log
from ivcommons.patterns.observer import Observer

from twisted.internet import reactor

from cccp.protocols.errors import SubscriptionError

log = Log("cccp.protocols.rt.subscriber")


class BasicSubscription(Observer, object):
    def __init__(self, subscriber, id):
        self.subscriber = subscriber
        self.id = id
        self.subjects = []

    def cancel(self):
        for subject in self.subjects:
            try:
                subject.detach(self)
            except Exception as e:
                log.warn("Canceling subject indicator {%s} from"
                         " subscription failed: %s" % (
                            subject.name, str(e)))
                log.info("Subject indicator {%s} has '%s' observers" % (
                            subject.name, subject.count_observers()))

    def add_subject(self, subject):
        if subject not in self.subjects:
            self.subjects.append(subject)
            subject.attach(self)

    def add_subjects(self, subjects):
        for subject in subjects:
            self.add_subject(subject)

    def del_subject(self, subject):
        if subject in self.subjects:
            self.subjects.remove(subject)
            subject.detach(self)

    def del_subjects(self, subjects):
        for subject in subjects:
            self.del_subject(subject)


class Subscription(BasicSubscription, object):
    def __init__(self, subscriber, id, target, type, profile, subjects):
        super(Subscription, self).__init__(subscriber, id)
        self.target = target
        self.type = type
        self.profile = profile
        self.deferred_call = None
        self.values_buffer = {}
        self.add_subjects(subjects)
        self.listenable_indicators = []

    def update(self, subject):
        if self.type != 'profile':
            if not self.deferred_call:
                self.deferred_call = reactor.callLater(0.1, self.update_later)
            self.values_buffer.update(subject.get())
        else:
            _list = subject.get()
            _values = []
            for row in _list:
                _row = {}
                for name in row:
                    if name in self.listenable_indicators:
                        _row[name] = row[name]
                if len(_row) > 1:
                    _values.append(_row)

            if _values:
                self.subscriber.prepareToSend(self.id, self.type, _values)

    def update_later(self):
        if self.values_buffer:
            self.subscriber.prepareToSend(self.id, self.type,
                                          self.values_buffer)
        self.deferred_call = None
        self.values_buffer = {}

    def add_listenable_indicators(self, indicators_list):
        self.listenable_indicators.extend(indicators_list)
        self.listenable_indicators = list(set(self.listenable_indicators))

    def del_listenable_indicators(self, indicators_list):
        _listenable_indicators = list(self.listenable_indicators)
        for indicator_name in indicators_list:
            try:
                _listenable_indicators.remove(indicator_name)
            except ValueError:
                raise LookupError(
                    'Indicator %s not subscribed.' % indicator_name
                )

        self.listenable_indicators = _listenable_indicators


class RecordSubscription(BasicSubscription, object):
    def __init__(self, subscriber, id):
        super(RecordSubscription, self).__init__(subscriber, id)

    def update(self, subject):
        values = subject.get()
        if isinstance(values, dict):
            indicator = values['record_indicator']
            self.queues_identifier(indicator)
            _values = [indicator]

        else:
            _accepted_records = {}
            for row in values:
                indicator = row['data'].get('record_indicator')
                if indicator and indicator['uri'] not in _accepted_records:
                    self.queues_identifier(indicator)
                    for accepted_indicator in [
                        'agent_session_ids', 'agent_logins',
                        'agent_display_names', 'agent_profile_names'
                    ]:
                        if accepted_indicator in indicator:
                            indicator[accepted_indicator] = indicator[
                                accepted_indicator]

                        indicator.setdefault('communication_type', 'inbound')
                        _accepted_records[indicator['uri']] = indicator
            _values = _accepted_records.values()

        for row in _values:
            self.subscriber.send_record_values(row)

    def queues_identifier(self, indicator):
        queue_name = indicator.get('queue')
        if queue_name:
            table = self.subscriber._indicator_lut.get_queues_table()
            indicator['queue_display_name'] = table.get(queue_name, queue_name)


class AutoRecordSubscription(BasicSubscription, object):
    def __init__(self, subscriber, id):
        super(AutoRecordSubscription, self).__init__(subscriber, id)

    def update(self, subject):
        values = subject.get()
        # TODO: Do last_record
        self.subscriber.send_autorecord_values(values)


class HistorySubscription(BasicSubscription, object):
    def __init__(self, subscriber, id):
        super(HistorySubscription, self).__init__(subscriber, id)

    def update(self, subject):
        values = subject.get()
        self.subscriber.send_history_values(values)


class CommunicationSubscription(BasicSubscription, object):

    def __init__(self, subscriber, target, id, indicators_list,
                 profiles_list, queues_list):
        super(CommunicationSubscription, self).__init__(subscriber, id)
        self.listenable_profiles = profiles_list
        self.listenable_queues = queues_list
        self.deferred_call = None
        self.type = "communication"
        self.target = target
        self.values_buffer = []
        self.communications = []
        self.listenable_indicators = indicators_list
        self.clistener = \
            self.subscriber._indicator_lut.get_communication_listener()
        self.add_subject(self.clistener)

    def update(self, subject):
        try:
            values = subject.get()
            self.extract_data_from_values(values)
            if not self.deferred_call:
                self.deferred_call = reactor.callLater(0.2, self.update_later)

        except Exception:
            log.error("Failsafe catched an unhandled exception.")
            log.exception()

    def update_later(self):
        if self.values_buffer:
            self.subscriber.prepareToSend(self.id, self.type,
                                          self.values_buffer)

        self.deferred_call = None
        self.values_buffer = []

    def in_scope(self, queue, profile, queue_scope, profile_scope):
        if profile:
            return profile in profile_scope
        elif queue:
            return queue in queue_scope
        return False

    def extract_data_from_values(self, values):
        for row in values:
            ###
            current_queue = row['current_queue_name']
            current_profile = row['current_profile_name']
            previous_queue = row['previous_queue_name']
            previous_profile = row['previous_profile_name']
            is_waiting = row['is_waiting']
            ###
            communication_id = row['data']['communication_id']
            task_id = row['data']['communication_task_id']['value']
            if not self.clistener.has_communication(communication_id):
                log.warn("Received indicators update for unknown "
                         "Communication '%s': %s" % (
                            communication_id, repr(row)))
                continue

            communication = self.clistener.get_communication(communication_id)
            current_scope = communication.check_scope(
                self.listenable_queues, self.listenable_profiles)
            previous_scope = row['data'][
                'communication_id'] in self.communications

            if 'task_end_date' in row['data'] and row['data'][
                    'task_end_date']['value']:
                current_scope, task_end = communication.check_end_scope(
                    self.listenable_queues, self.listenable_profiles)
                if current_scope and task_end:
                    if communication_id in self.communications:
                        self.communications.remove(communication_id)
                        data = deepcopy(row['data'])
                        reactor.callLater(5,
                                          self.clistener.clean_communication,
                                          communication_id, task_id)
                        self.values_buffer.append(data)

                    elif not previous_scope:
                        data = deepcopy(row['data'])
                        reactor.callLater(5,
                                          self.clistener.clean_communication,
                                          communication_id, task_id)
                        self.values_buffer.append(data)

                # Catch all
                if not current_queue and not current_profile \
                        and not previous_queue \
                        and not previous_profile \
                        and is_waiting and not current_scope \
                        and previous_scope:
                    self.communications.remove(communication_id)
                    data = deepcopy(row['data'])
                    self.values_buffer.append(data)

            else:
                if is_waiting:
                    if current_scope:
                        data = deepcopy(row['data'])
                        self.values_buffer.append(data)
                        if communication_id not in self.communications:
                            self.communications.append(communication_id)

                else:
                    if current_scope:
                        if communication_id not in self.communications:
                            self.communications.append(communication_id)
                            try:
                                data = self.clistener.get_task_values(
                                    task_id)['data']

                            except ValueError as e:
                                log.error(
                                    "get_task_values failed: %s " % str(e)
                                )
                                continue

                            except Exception as e:
                                log.exception()
                                continue

                        else:
                            data = deepcopy(row['data'])
                        self.values_buffer.append(data)

                    elif previous_scope:
                        data = deepcopy(row['data'])
                        data['task_end_date'] = {'value': "unmanageable"}
                        self.communications.remove(
                            row['data']['communication_id'])
                        reactor.callLater(5,
                                          self.clistener.clean_communication,
                                          communication_id, task_id)
                        self.values_buffer.append(data)

    def get_data_from_values(self, values):
        data = []
        for row in values:
            if row['current_queue_name'] in self.listenable_queues \
                    and not row['current_profile_name'] or \
                    row['current_profile_name'] in self.listenable_profiles:
                self.communications.append(row['data']['communication_id'])
                data.append(row['data'])
        return data

    def add_listenable_profiles(self, profiles_list):
        self.listenable_profiles.extend(profiles_list)
        self.listenable_profiles = list(set(self.listenable_profiles))

    def add_listenable_queues(self, queues_list):
        self.listenable_queues.extend(queues_list)
        self.listenable_queues = list(set(self.listenable_queues))

    def add_listenable_indicators(self, indicators_list):
        self.listenable_indicators.extend(indicators_list)
        self.listenable_indicators = list(set(self.listenable_indicators))

    def del_listenable_indicators(self, indicators_list):
        _listenable_indicators = list(self.listenable_indicators)
        for indicator_name in indicators_list:
            try:
                _listenable_indicators.remove(indicator_name)
            except ValueError:
                raise LookupError(
                    'Indicator %s not subscribed.' % indicator_name)
        self.listenable_indicators = _listenable_indicators


class Subscriber(object):
    def __init__(self, indicator_lut):
        self.subscriptions = {}
        self._indicator_lut = indicator_lut

    def subscribe(self, target, type, indicators=[], profile_name=None):
        subscription_id = compute_key('%s:%s' % (str(target), type))

        subjects = []
        try:
            subjects.extend(self._indicator_lut.get_indicators(
                                target, type, profile_name, indicators))

        except LookupError as e:
            log.error(str(e))
            raise SubscriptionError(str(e))

        self.subscriptions[subscription_id] = Subscription(
            self, subscription_id, target, type, profile_name, subjects)

        data = self.get_subscription_values(subscription_id, indicators)
        return {"id": subscription_id, "data": data}

    def subscribe_profile(self, target, _type, indicators_list):
        subscription_id = compute_key('%s:%s:profile' % (target, _type))
        try:
            profile = self._indicator_lut.add_profile_indicators(
                target, _type, indicators_list)
        except LookupError as e:
            log.error(str(e))
            raise SubscriptionError(str(e))

        self.subscriptions[subscription_id] = Subscription(
            self, subscription_id, target, "profile", target, [profile])
        data = self.get_subscription_values(subscription_id,
                                            indicators_list, _type=_type)
        _listenable = []
        if _type == "communication":
            _listenable.append('communication_id')
        else:
            _listenable.append('login')
        _listenable.extend(indicators_list)

        self.subscriptions[
            subscription_id
        ].add_listenable_indicators(_listenable)
        return {'id': subscription_id, 'data': data}

    def subscribe_communication(self, target, indicators_list, profiles_list,
                                queues_list):
        subscription_id = compute_key(
            '%s:%s:%s' % (
                str(len(profiles_list)), str(len(queues_list)),
                'communicationsvalues'))

        self.subscriptions[subscription_id] = CommunicationSubscription(
            self, target, subscription_id, indicators_list,
            profiles_list, queues_list)

        return {'id': subscription_id,
                'data': self.get_communications_values(
                    subscription_id, indicators_list)}

    def subscribe_record_values(self):
        subscription_id = compute_key('%s' % ('recordvalues'))
        self.subscriptions[subscription_id] = RecordSubscription(
            self, subscription_id)
        self._indicator_lut.set_record_indicators(
            self.subscriptions[subscription_id])

    def subscribe_autorecord_values(self):
        subscription_id = compute_key('%s' % ('autorecordvalues'))
        self.subscriptions[subscription_id] = AutoRecordSubscription(
            self, subscription_id)
        self._indicator_lut.set_autorecord_session_watchers(
            self.subscriptions[subscription_id])

    def subscribe_history_values(self):
        subscription_id = compute_key('%s' % ('historyvalues'))
        self.subscriptions[subscription_id] = HistorySubscription(
            self, subscription_id)
        self._indicator_lut.set_history_indicators(
            self.subscriptions[subscription_id])

    def get_subscription(self, subscription_id):
        if subscription_id in self.subscriptions:
            return self.subscriptions[subscription_id]

        else:
            message = "Unknown subscription id '%s'" % (subscription_id)
            log.error(message)
            raise SubscriptionError(message)

    def update_profile_indicators(self, subscription_id, _type,
                                  added_indicators=[],
                                  removed_indicators=[]):

        subscription = self.get_subscription(subscription_id)
        if removed_indicators:
            self._indicator_lut.del_profile_indicators(
                subscription.target, _type, removed_indicators)
            subscription.del_listenable_indicators(removed_indicators)

        if added_indicators:
            self._indicator_lut.add_profile_indicators(
                subscription.target, _type, added_indicators)
            subscription.add_listenable_indicators(added_indicators)
            return {
                'data': self.get_subscription_values(
                    subscription_id, added_indicators, _type=_type
                )
            }

    def update_communication_indicators(self, subscription_id,
                                        profiles_list=[], queues_list=[],
                                        added_indicators=[],
                                        removed_indicators=[]):
        subscription = self.get_subscription(subscription_id)
        if profiles_list:
            subscription.add_listenable_profiles(profiles_list)

        if queues_list:
            subscription.add_listenable_queues(queues_list)

        if removed_indicators:
            subscription.del_listenable_indicators(removed_indicators)

        if added_indicators:
            subscription.add_listenable_indicators(added_indicators)
            return {'data': self.get_communications_values(subscription_id,
                    subscription.listenable_indicators)}

    def update_subscription(self, subscription_id, added_indicators,
                            removed_indicators):
        subscription = self.get_subscription(subscription_id)

        try:
            added_subjects = self._indicator_lut.get_indicators(
                subscription.target, subscription.type,
                subscription.profile, added_indicators)
            removed_subjects = self._indicator_lut.get_indicators(
                subscription.target, subscription.type,
                subscription.profile, removed_indicators)

        except LookupError as e:
            log.error(str(e))
            raise SubscriptionError(str(e))

        subscription.add_subjects(added_subjects)
        subscription.del_subjects(removed_subjects)
        if added_indicators:
            return self.get_subscription_values(subscription_id,
                                                added_indicators)

    def get_subscription_values(self, subscription_id, indicators, _type=None):
        data = {}
        subscription = self.subscriptions[subscription_id]
        if subscription.type != "profile":
            for indicator in indicators:
                try:
                    _indicator = self._indicator_lut.get_indicators(
                        subscription.target, subscription.type,
                        subscription.profile, [indicator])[0]
                except LookupError as e:
                    log.error(str(e))
                    raise SubscriptionError(str(e))

                data[indicator] = _indicator.get()[indicator]

        else:
            if not self._indicator_lut.has_profile(subscription.target):
                profile = self._indicator_lut.add_profile(subscription.target)
            else:
                profile = self._indicator_lut.get_profile(subscription.target)
            data = profile.get_values(_type, indicators_filtered=indicators)

        return data

    def get_communications_values(self, subscription_id, indicators=[]):
        values = self._indicator_lut.get_communication_listener().get_values(
            indicators)
        return self.subscriptions[subscription_id].get_data_from_values(values)

    def unsubscribe(self, subscription_id):
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].cancel()
            del self.subscriptions[subscription_id]
        else:
            message = "Unknown subscription id '%s'" % (subscription_id)
            log.error(message)
            raise SubscriptionError(message)

    def unsubscribe_all(self):
        for subscription_id in dict(self.subscriptions):
            self.subscriptions[subscription_id].cancel()
            del self.subscriptions[subscription_id]

    def prepareToSend(self, subscription_id, _type, indicators_value):
        try:
            target = self.subscriptions[subscription_id].target
        except KeyError:
            log.error(
                "Sending data failed, subscription_id(%s) is unknown: "
                "type=%s data=%s" % (subscription_id, _type, indicators_value)
            )
            return
        self.send(_type, target, indicators_value)

    def send(self, type, target, indicators_value, ):
        raise NotImplementedError()

    def send_record_values(self, values):
        raise NotImplementedError()

    def send_autorecord_values(self, values):
        raise NotImplementedError()

    def send_history_values(self, values):
        raise NotImplementedError()

    def reset(self, log=log):
        self._indicator_lut.reset(log=log)
