#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""Simple Logging Module for CCCP Deployment."""

import sys
import os
from datetime import datetime


class Log(object):
    """Simple logging class for CCCP deployment."""

    def __init__(self, name):
        self.name = name

    def _log(self, level, message):
        """Internal log method."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level:<8} {self.name}: {message}")

    def system_message(self, message):
        """Log system message."""
        self._log("SYSTEM", message)

    def error_message(self, message):
        """Log error message."""
        self._log("ERROR", message)

    def warning_message(self, message):
        """Log warning message."""
        self._log("WARNING", message)

    def info_message(self, message):
        """Log info message."""
        self._log("INFO", message)

    def debug_message(self, message):
        """Log debug message."""
        self._log("DEBUG", message)

    # Alias methods to maintain compatibility
    def system(self, message):
        self.system_message(message)

    def error(self, message):
        self.error_message(message)

    def warning(self, message):
        self.warning_message(message)

    def info(self, message):
        self.info_message(message)

    def debug(self, message):
        self.debug_message(message)


# Create a global logger for compatibility
def get_logger(name):
    """Get logger instance."""
    return Log(name)
