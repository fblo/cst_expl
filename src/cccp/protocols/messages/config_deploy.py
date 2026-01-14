#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's mcanal libraries.
# Interact-IV.com (c) 2013-2016
#
# Contact: softeam@interact-iv.com
# Authors:
#    - JTAG <jtag@interact-iv.com>

"""CCXML Configuration Deployment Messages."""

# Configuration deployment message types
initialize = 0x40000002

# Deployment request messages
config_deploy_request = 10030
config_deploy_response = 20030
config_validate_request = 10031
config_validate_response = 20031
config_backup_request = 10032
config_backup_response = 20032
config_rollback_request = 10033
config_rollback_response = 20033

# Configuration chunk messages (for large files)
config_chunk_request = 10034
config_chunk_response = 20034

# Permission and rights requests
deployment_rights_request = 10035
deployment_rights_response = 20035

# Status and monitoring
deployment_status_request = 10036
deployment_status_response = 20036
