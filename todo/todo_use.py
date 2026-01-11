#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#	- PEMO <pemo@interact-iv.com>

# This is the todo list !!
# You have to write the feature, implement it, test it and move the import sys;sys.exit() "cursor"
# to the next one.
# When you finish to implement a module, create the unittest based on the feature list and write
# some examples or documentation...
# Isn't it some effective eXtreme Programming ? No, just the Art of Software Development for Idlers.

import cccp.usage

db = cccp.usage.database("10.199.8.42",20024)

#db.users("filtre")["index"].
print db.sessions()
s = cccp.usage.CallSession()
print s.fields()
 
print db.sessions(fields="",filter="")

