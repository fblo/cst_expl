#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from cccp.protocols.ccthread import CDEPSocket
import cccp.protocols.messages.user_control as msg
import cccp.protocols.messages.explorer as msge


class user_control:
    def __init__(self, address, port):
        self.socket = CDEPSocket(self, address, port, msg.initialize)
        self.socket.start()
        self.socket.send(msg.initialize, 1234)

    def step(self):
        self.socket.step_result = None
        return self.socket.step()

    def step_done(self, step_result=None):
        self.socket.step_done(step_result)

    def stop(self):
        self.socket.stop()
        self.socket.join()

    @property
    def step_result(self):
        return self.socket.step_result

    def add_session(
        self,
        session_id,
        login,
        password,
        instances_count,
        has_been_connected,
        client_version,
        cookie,
    ):
        self.socket.send(
            msg.add_session,
            session_id,
            login,
            password,
            instances_count,
            has_been_connected,
            client_version,
            cookie,
        )

    def logout(self, session_id):
        self.socket.send(msg.logout, session_id)

    def client_event(self, session_id, source, target, delay, event_name, event_object):
        self.socket.send(
            msg.client_event,
            session_id,
            source,
            target,
            delay,
            event_name,
            event_object,
        )

    def on_server_event(
        self, session_id, source, target, delay, event_name, event_object
    ):
        # We make event_name shorter : Remove "com.consistent.ccenter" possibly followed by ".user"
        if len(event_name) < 27:
            raise self.CcxmlServerSubscriberError("Event name unknown: %s" % event_name)
        event_name = event_name[23:]
        if event_name[:4] == "user":
            event_name = event_name[5:]

        # Specific handling for "state" event which is a piece of ...
        if len(event_name) >= 5:
            if event_name[:5] == "state":
                event_name, state_name = tuple(event_name.split("."))
                if event_name == "state" or event_name == "state_ok":
                    if len(state_name) > 6:
                        if state_name[:6] == "pause_":
                            pause_name = state_name
                            self.event_handler.on_change_state("pause", pause_name)
                            return
                    self.event_handler.on_change_state(state_name)
                    return
                print(state_name + " doesn't exist")  # Case of state_forbidden.* event.
                return

        # And now just call the event handler (=a method of the user)  which has got the same name as the event from consistent
        method_name = "on_" + event_name.replace(".", "_")
        if hasattr(self.event_handler, method_name):
            f = getattr(self.event_handler, method_name)
            if event_object is not None:
                f(event_object)
            else:
                f()
        else:
            print("WARNING:", method_name, "not defined !")
            if event_object is not None:
                print(event_object)


class ccxml_explorer:
    def __init__(self, address, port):
        self.socket = CDEPSocket(self, address, port, msge.initialize)
        self.socket.start()
        self.socket.send(
            msge.initialize, 1234, True
        )  # client_version fixe et can_compress

    def step(self):
        self.socket.step_result = None
        return self.socket.step()

    def step_done(self, step_result=None):
        self.socket.step_done(step_result)

    @property
    def step_result(self):
        return self.socket.step_result

    def stop(self):
        self.socket.stop()
        self.socket.join()

    def login(self, session_id, login, password, instances_count, has_been_connected):
        self.socket.send(
            msge.login, session_id, login, password, instances_count, has_been_connected
        )

    def logout(self, session_id):
        self.socket.send(msge.logout, session_id)

    def client_event(self, session_id, path, source, target, delay, event_name, object):
        self.socket.send(
            msge.client_event,
            session_id,
            path,
            source,
            target,
            delay,
            event_name,
            object,
        )
