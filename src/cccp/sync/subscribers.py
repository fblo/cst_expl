#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from cccp.protocols.clients.ccxml import user_control, ccxml_explorer
from cccp.protocols.clients.dispatch import dispatch_explorer
from cccp.protocols.converter import Converter

import logging as log

# log.basicConfig(level=log.DEBUG)


class ICcxmlEventHandler:
    def on_logout(self):
        pass


class CcxmlSubscriber(user_control):
    def __init__(self, ip, port, event_handler=None):
        self.ip = ip
        self.port = port
        user_control.__init__(self, self.ip, self.port)
        self.event_handler = event_handler
        # self.logged = False

    def on_connection_ok(self, server_version):
        log.debug("CcxmlSubscriber connexion ok : %s" % server_version)

    def login(self, login, password):
        # if self.logged:
        #    raise CcxmlSubscriberError("CcxmlSubscriber can logged only one user, please logout first.")
        self.add_session(1, login, password, 1, False, 1234, "")
        return self.step()
        # if self.step_result[0] == True: self.logged = True
        # return self.step_result

    def on_reject(self, session_id, reason):
        self.step_done((False, reason))
        # print "on_reject"
        log.debug("on_reject :%s" % reason)

    def on_login_ok(
        self, session_id, user_id, explorer_id, interface_name, so_mark, tos
    ):
        self._explorer_id = explorer_id
        self._user_id = user_id
        self.step_done((True, user_id))
        # print "on_login_ok"
        log.debug("on_login_ok")

    def logout(self):
        user_control.logout(self, 1)
        return True
        # return self.step()

    def on_logout_ok(self, session_id):
        # self.step_done(True)
        log.debug("on_logout_ok")

    def send_event(self, name, data=None):
        name = "com.consistent.ccenter." + name
        # import sys; sys.stdout.write(str(vars(self)))
        self.client_event(1, self._explorer_id, self._user_id, 0.0, name, data)


class CcxmlRequester(ccxml_explorer):
    def __init__(self, ip, port, event_handler=None):
        self.ip = ip
        self.port = port
        ccxml_explorer.__init__(self, self.ip, self.port)

    def on_connection_ok(self, server_version, date):
        log.debug("CcxmlRequester connexion ok : %s" % server_version)

    def login(self, login, password):
        ccxml_explorer.login(self, 1, login, password, 0, False)
        return self.step()

    def on_login_ok(self, session_id, user_id, explorer_id):
        self.step_done((True, user_id))
        log.debug("on_login_ok")

    def on_reject(self, session_id, reason):
        self.step_done((False, reason))
        log.debug("on_reject :%s" % reason)

    def logout(self):
        ccxml_explorer.logout(self, 1)
        return True
        # return self.step()

    def send_event(self, name, target, data=None, source=""):
        name = "com.consistent.ccenter." + name
        self.client_event(1, "", source, target, 0.0, name, data)


class IDispatchViewConsumer:
    def on_view_change(self, line_id, line):
        pass

    def on_view_delete(self, line_id):
        pass


class DispatchSubscriber(dispatch_explorer):
    next_idx = 1

    def __init__(self, ip, port):
        self.tables = {}
        self.next_format_id = 1
        self.ip = ip
        self.port = port
        self.converter = Converter()
        dispatch_explorer.__init__(self, self.ip, self.port)

    def set_format(self, format):
        if format == "":
            return 0
        cst_format = self.converter.create_cst_object(format)[0]
        cst_format.format_id = self.next_format_id
        self.next_format_id += 1
        dispatch_explorer.set_object_format(self, 1, cst_format)
        return cst_format.format_id

    def start_view(
        self,
        db_root,
        format="",
        filter="",
        view={},
        view_consumer=IDispatchViewConsumer(),
    ):
        format_id = self.set_format(format)
        defaults = self.compute_defaults(format)
        idx = self.next_idx
        view[0] = format
        self.tables[idx] = (view, format_id, view_consumer, defaults)
        self.query_list(1, idx, "/dispatch", 0, db_root, filter, 0, "", 0)
        self.next_idx += 1
        return idx

    def compute_defaults(self, format):
        f = []
        for s in format:
            try:
                if s[-5:] == "count":
                    f.append(0)
                elif s[-5:] == "_date":
                    f.append(None)
                elif s[-8:] == "duration":
                    f.append(0)
                else:
                    f.append("")
            except:
                f.append("")
        return f

    def stop_view(self, idx):
        self.stop_query(1, idx)
        del self.tables[idx]

    def on_list_response(self, session_id, idx, object):
        view, format_id, view_consumer, defaults = self.tables[idx]
        for item in object.items:
            obj_id = item.item_id
            if item.action == 2:
                if obj_id in view:
                    del view[obj_id]
                    view_consumer.on_view_delete(obj_id)
                    return
            if obj_id not in view:
                view[obj_id] = list(defaults)
            if format_id > 0:
                self.query_object(1, idx, "/dispatch", obj_id, format_id, obj_id)
            else:
                view_consumer.on_view_change(obj_id, None)

    def on_object_response(self, session_id, idx, obj, obj_id):
        view, _, view_consumer, _ = self.tables[idx]
        d = view[obj_id]
        for e in obj.values:
            if hasattr(e, "value"):
                d[e.field_index] = e.value
        view_consumer.on_view_change(obj_id, d)
