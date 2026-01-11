#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>
#    - SLAU <slau@interact-iv.com>

from cccp.sync.db import ConfigDB, UsageDB
from cccp.sync.process import ProcessViewer
from cccp.sync.session import SessionManager

class Project:
    def __init__(self,name,ip="127.0.0.1"):
        self.name = name
        self.config = ProjectConfig(name,ip)
        self.process = ProcessViewer(ip=ip).project(name)
        self.usage = UsageDB(name,host=ip,port=self.process.dispatch.port)
        self.session = SessionManager(name, ip=ip, port=self.process.ccxml.port)

class ProjectConfig(ConfigDB):
    def __init__(self,name,ip=None):
        self.name = name
        self.basepath = "/db/projects/"+name+"/"
        ConfigDB.__init__(self,ip)

    def _full_path(self,path):
        if len(path) > 3:
            if path[:3] == "/db":
                return path
        return self.basepath+path

    def list(self,path=""):
        if path!="":
            path = self._full_path(path)
        else:
            path = self.basepath[:-1]
        return ConfigDB.list(self,path)

    def create(self,path):
        return ConfigDB.create(self,self._full_path(path))

    def delete(self,path):
        return ConfigDB.delete(self,self._full_path(path))

    def is_empty(self,path):
        return ConfigDB.is_empty(self,self._full_path(path))

    def exists(self,path):
        return ConfigDB.exists(self,self._full_path(path))

    def move(self,path,new_path):
        return ConfigDB.move(self,self._full_path(path),self._full_path(new_path))

    def copy(self,path,new_path):
        return ConfigDB.copy(self,self._full_path(path),self._full_path(new_path))

    def get(self,path,builtin_mode=False):
        return ConfigDB.get(self,self._full_path(path),builtin_mode=False)

    def put(self,path,objects):
        return ConfigDB.put(self,self._full_path(path),objects)
