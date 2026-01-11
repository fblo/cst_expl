#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - SLAU <slau@interact-iv.com>

class consistent_process:
    def __init__(self):
        self.id = 0 # AUTO_ID
        self.max_stop_duration = 2000
        self.max_respawn_count = 5
        self.max_respawn_duration = 10000
        self.retry_interval = 2000
        self.big_retry_interval = 5000

class consistent_head_process(consistent_process):
    def __init__(self, is_main = False):
        self.class_name = "head"
        self.process_name = "consistent_head"

        if is_main:
            self.listen_port = 20000
            self.first_dynamic_port = 20000
            self.last_dynamic_port = 20500

class ccenter_voip_process(consistent_process):
    pass

class ccenter_proxy_process(consistent_process):
    pass

class ccenter_ccxml_process(consistent_process):
    pass

class ccenter_dispatch_process(consistent_process):
    pass

class consistent_logger_process(consistent_process):
    pass

class ccenter_dispatch_process(consistent_process):
    pass

class ccenter_queues_process(consistent_process):
    pass

class ccenter_scheduler_process(consistent_process):
    pass

class consistent_store_process(consistent_process):
    pass

