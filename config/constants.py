#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##
# Copyright 2017 FIWARE Foundation, e.V.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##

__author__ = 'fla'

GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'
APPLICATION_NAME = 'TSC Enablers Dashboard'
CREDENTIAL_DIR = '.credentials'
CREDENTIAL_FILE = 'sheets.googleapis.com.json'
DB_NAME = 'enablers-dashboard.db'
DB_FOLDER = 'dbase'
LOG_FILE = 'tsc-dashboard.log'

# We need to add 16 rows in the number of enablers list corresponding to:
# - Title
# - Report date
# - Data sources updated on
# - Source
# - Units
# - Enabler Impl
# - INCUBATED
# - DEVELOPMENT
# - SUPPORT
# - DEPRECATED
# - And 6 extra blank rows between them
FIXED_ROWS = 16

# We keep the firsts row without change in the sheet (sheet title)
INITIAL_ROW = 2

# The number of columns to delete corresponds to:
# Source, Catalogue, Readthedocs, Docker, GitHub, Coverall, Academy, Helpdesk, Backlog, ForgeWiki, Lab
FIXED_COLUMNS = 9

# We start to delete from the initial column
INITIAL_COLUMN = 1
