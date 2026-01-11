#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2015
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>
#
# Inspired from: https://docs.python.org/2.5/lib/tzinfo-examples.txt

from datetime import datetime, timedelta, tzinfo

ZERO = timedelta(0)
HOUR = timedelta(hours=1)

import time as _time

STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET


class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

Local = LocalTimezone()

def date_to_iso(date=None):
    if date:
        return date.isoformat()

    else:
        return datetime.now().replace(tzinfo=Local).isoformat()
