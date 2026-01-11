#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from cccp.sync.subscribers import CcxmlSubscriber, CcxmlRequester
from cccp.sync.process import ProcessViewer


class SessionManager:
    def __init__(self, project, server="", ip="localhost", port=0):
        self.ip = ip
        self.project = project
        self.server = server
        if port == 0:
            self.port = ProcessViewer(ip=ip).project(project).ccxml.port
        else:
            self.port = port

    def login(self, name, password):
        self.login_name = name
        self.password = password
        self.subscriber = CcxmlSubscriber(self.ip, self.port, self)
        return self.subscriber.login(name, password)

    def logout(self):
        result = self.subscriber.logout()
        self.subscriber.stop()
        return result

    def user_logout(self, user_sid, sup_login, sup_password):
        print("user_logout with %s/%s" % (sup_login, sup_password))
        r = CcxmlRequester(self.ip, self.port)
        result, _ = r.login(sup_login, sup_password)
        if not result:
            print("login failed")
            r.stop()
            return False
        print("login done, send user_logout")
        r.send_event("user.logout", user_sid)
        r.logout()
        r.stop()
        return True
