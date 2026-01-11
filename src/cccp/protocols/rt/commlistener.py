#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from twisted.internet import reactor

from cccp.protocols.rt.subscription import (
    Subscribable,
    Communication,
    Task,
)

from ivcommons.log import Log


log = Log("cccp.protocols.rt.communicationlistener")


class CommunicationListener(Subscribable):
    def __init__(self):
        super(CommunicationListener, self).__init__()
        self.communications = {}
        self.tasks = {}

        self.values = []
        self.deferredCall = None

    def has_communication(self, communication_id):
        return communication_id in self.communications

    def add_communication(self, communication_id,
                          communication_type="inbound"):
        if not self.has_communication(communication_id):
            self.communications[communication_id] = Communication(
                communication_id, self, communication_type=communication_type
            )
            self.add_subject(self.communications[communication_id])

    def get_communication(self, communication_id):
        return self.communications[communication_id]

    def del_communication(self, communication_id):
        if communication_id in self.communications:
            _communication = self.communications[communication_id]
            if _communication.has_tasks():
                _communication.clean_tasks()

            if _communication in self.subjects:
                self.del_subject(_communication)

            del self.communications[communication_id]

    def del_task(self, task_id):
        if task_id in self.tasks:
            self.del_subject(self.tasks[task_id])
            del self.tasks[task_id]

    def clean_communication(self, communication_id, task_id):
        if communication_id in self.communications:
            if self.communications[communication_id].remove_task(task_id):
                if not self.communications[communication_id].has_tasks():
                    del self.communications[communication_id]

    def get_task_values(self, task_id):
        if task_id in self.tasks:
            return self.tasks[task_id].get_values()

        else:
            raise ValueError("Unknown task_id: [%s]" % task_id)

    def add_subject(self, subject):
        self.subjects.append(subject)
        subject.attach(self)

    def del_subject(self, subject):
        self.subjects.remove(subject)
        subject.detach(self)

    def update(self, subject):
        values = subject.get()
        try:
            if subject.is_task():
                communication = self.communications[values[
                    'data']['communication_id']]
                values = communication.validate_task(subject, values)

            if values:
                self.values.append(values)
                if not self.deferredCall:
                    self.deferredCall = reactor.callLater(
                        0.2,
                        self.delayedNotification
                    )

        except KeyError:
            log.error(
                "Can't find communication, can't apply update: %s" % (
                    repr(values),
                )
            )

    def delayedNotification(self):
        self.notify()
        self.values = []
        self.deferredCall = None

    def get(self):
        return self.values

    def get_values(self, indicators_filtered):
        values = []
        for communication in self.tasks.values():
            row = communication.get_values(
                indicators_filtered
            )
            if len(row['data']) > 2:
                values.append(row)

        return values

    def get_communication_list(self, profiles_list, queues_list):
        communication_list = []
        for communication in self.tasks.values():
            current_queue = communication.current_queue.value
            current_profile = communication.current_profile.value

            if current_queue in queues_list or \
                    current_profile in profiles_list:

                if not communication.indicators["end_date"].value:
                    communication_list.append(
                        {
                            'communication_id': communication.call_id,
                            'channel': 'iv-vocal'
                        }
                    )
        return communication_list

    def apply_task_data(self, data):
        task_id = data['task_id']
        communication_id = data['parent_call_session_id']

        if task_id in self.tasks:
            self.tasks[task_id].apply_data(data)

        else:
            if communication_id in self.communications:
                communication = self.communications[communication_id]

                if communication_id in self.communications and \
                        communication in self.subjects:
                    self.del_subject(communication)

                communication_data = communication.get_values(
                    [
                        'to', 'from', 'communication_create_date',
                        'previous_queue_name',
                        'previous_profile_name'
                    ]
                )['data']
                del communication_data['communication_task_id']
                task = Task(communication_id, data, communication_data,
                            communication_type = communication.communication_type) # NOQA
                self.tasks[task_id] = task
                communication.bind_task(task)

                self.add_subject(task)
