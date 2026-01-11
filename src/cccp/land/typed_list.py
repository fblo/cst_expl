#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

class typed_list(list):
    content_type=""
    def append(self, item):
        if self.content_type=="":
            self.content_type=type(item).__name__
        else:
            if type(item).__name__ != self.content_type:
                raise TypeError
        list.append(self,item)

