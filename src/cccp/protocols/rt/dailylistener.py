#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2017
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>


class DailyListener(object):

    allowed_indicators = (
        'total_leg_count.value',
        'contacted_leg_count.value',
        'failed_leg_count.value',
        'canceled_leg_count.value',
        'outbound_contact_duration.value',
        'outbound_max_contact_duration.value',
    )

    def __init__(self):
        self.data = {}

    def reset(self):
        self.data = {}

    def apply_data(self, profile_name, user_login, session_id, data):
        for indicator in data:
            if indicator in self.allowed_indicators:
                self.data.setdefault(profile_name, {}).setdefault(
                    user_login, {}).setdefault(indicator, {})[
                        session_id] = data[indicator]

    def get_indicator_value(self, profile_name, user_login, indicator_name):
        if indicator_name not in self.allowed_indicators:
            return []

        return self.data.get(profile_name, {}).get(
            user_login, {}).get(indicator_name, {})
