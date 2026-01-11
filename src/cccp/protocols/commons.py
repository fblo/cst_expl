#!/usr/bin/env python

# This file is part of Interact-IV's Middleware Server.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>
#    - GRIC <gric@interact-iv.com>
#    - PEMO <pemo@interact-iv.com>

class IncrementIdReservation(object):
    def __init__(self):
        self.max_id = 0
        self.ids_released = []

    def reserve(self):
        if len(self.ids_released) == 0:
            self.max_id += 1
            return self.max_id
        else:
            i = self.ids_released.pop()
            return i

    def release(self,id):
        self.ids_released.append(id)
