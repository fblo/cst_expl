#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from ivcommons.log import Log

log = Log("cccp.protocols.ccxml")


class BaseCcxmlClient(object):
    """
    This class will be used to get and send events to Ccxml server.

    Four methods will be called back to an event sent by the Ccxml.
    They need to be linked to a real method.
    * get_login_ok
    * get logout_ok
    * get_reject
    * get_server_event
    """
    def get_login_ok(self, session_id, user_id, explorer_id):
        """
        This method will be called back by the event login_ok,
        which mean the agent has successfully logged to iv2us-core.

        This method must to be linked to a real method.

        :param session_id: Session ID.
        :type session_id: str
        :param user_id: User ID.
        :type user_id: str
        :param explorer_id: Explorer ID.
        :type explorer_id: str
        """
        raise Exception("Not defined")

    def get_logout_ok(self, session_id):
        """
        This method will be called back by the event logout_ok,
        which mean the agent has successfully logout from iv2us-core.

        This method must to be linked to a real method.

        :param session_id: Session ID.
        :type session_id: str
        """
        raise Exception("Not defined")

    def get_reject(self, session_id, reason):
        """
        This method will be called back by the event reject,

        This method must to be linked to a real method.

        :param session_id: Session ID.
        :type session_id: str
        :param reason: The reason why its rejected.
        :type reason: str
        """
        raise Exception("Not defined")

    def get_server_event(self, session_id, event_name, event_object):
        """
        This method will be called back by the event server_event,
        This event is used to carry events to users.

        This method must be linked to a real method.

        :param session_id: Session ID.
        :type session_id: str
        :param event_name: Event name sent by Ccxml server.
        :type event_name: str
        :param event_object: Object associated to the event, it may
                             be empty. (= None)
        :type event_object: dict
        """
        raise Exception("Not defined")

    def send_client_event(self, session_id, source, target,
                          event_name, event_object=None):
        """
        This method will be used by the client to send event to
        the Ccxml server.
        The event object is optional, many events dont have it,
        it is used to carry options.

        :param session_id: Session ID.
        :type session_id: str
        :param source: Source.
        :type source: str
        :param target: Target.
        :type target: str
        :param event_name: Event name.
        :type event_name: str
        :param event_object: Event object.
        :type event_object: dict
        """
        self.client_event(session_id, source, target, event_name, event_object)

    def send_login(self, session_id, login, password, was_connected=False):
        """
        This method will be used by the client to connect an user to
        the Ccxml server.

        :param session_id: Session ID.
        :type session_id: str
        :param login: Login of the user.
        :type login: str
        :param password: Password of the user.
        :type password: str
        :param was_connected: If the user was reconnected
                              (Need to check the real usage of this param)
        :type was_connected: boolean
        """
        self.add_session(session_id, login, password, was_connected)

    def send_logout(self, session_id):
        """
        This method is used by the client to logout an user from
        the Ccxml server.

        :param session_id: Session ID.
        :type session_id: str
        """
        self.logout(session_id)

    def send_disconnected(self, session_id):
        """
        This method is used by the client to set an user in disconnected
        (unplug) state from Ccxml server.

        :param session_id: Session ID.
        :type session_id: str
        """
        self.disconnected(session_id)

    def add_session(self, session_id, login, password, was_connected):
        raise Exception("Not defined")

    def client_event(self, session_id, source, target, event_name,
                     event_object):
        raise Exception("Not defined")

    def disconnected(self, session_id):
        raise Exception("Not defined")

    def login(self, session_id, login, password, was_connected):
        raise Exception("Not defined")

    def logout(self, session_id):
        raise Exception("Not defined")
