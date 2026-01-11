#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

class indexed_objects_dict(dict):
    def add(self,u):
        self[u.idx] = u
        u.dict = self

#
# This class purpose is only serve as interface
# Be aware that if you don't inherit from object, setter property doesn't work !! Is it a python bug ?
#
class indexed_object(object):
    def __init__(self, get_idx, set_idx):
        self._get_idx = get_idx
        self._set_idx = set_idx
        self.dict = None
    def get_idx(self):
        return self._get_idx()
    def set_idx(self, value):
        self._set_idx(value)
    def set_dict_idx(self, old_value):
        if self.dict is None: return
        del self.dict[old_value]
        self.dict.add(self)
    idx = property(get_idx, set_idx)
    def __eq__(self,other):
        return self.idx == other.idx


