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

from configparser import ConfigParser
import logging
import os.path

__author__ = 'fla'

__version__ = '2.2.0'


"""
Default configuration.

The configuration `cfg_defaults` are loaded from `cfg_filename`, if file exists in
/etc/fiware.d/tsc-dashboard.ini

Optionally, user can specify the file location manually using an Environment variable
called TSC_DASHBOARD_SETTINGS_FILE.
"""

name = 'tsc-dashboard'

cfg_dir = "/etc/fiware.d"

if os.environ.get("TSC_DASHBOARD_SETTINGS_FILE"):
    cfg_filename = os.environ.get("TSC_DASHBOARD_SETTINGS_FILE")
    cfg_dir = os.path.dirname(cfg_filename)

else:
    cfg_filename = os.path.join(cfg_dir, '%s.ini' % name)

Config = ConfigParser()

Config.read(cfg_filename)


def config_section_map(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


def check_log_level(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)

    if not isinstance(numeric_level, int):
        print('Invalid log level: {}'.format(loglevel))
        exit()

    return numeric_level


def check_metric_values(metric_values):

    if metric_values.upper() not in ('UPDATE', 'READ'):
        msg = '\nERROR: param metricvalues in file tsc-dashboard.ini has not a valid value. ' \
              '\n       Accepted values are only "read" or "update".' \
              '\n\n       Please update the configuration file.'
        exit(msg)

    return metric_values


if Config.sections():
    # Data from Google section
    google_section = config_section_map("google")

    CREDENTIAL = os.path.join(cfg_dir, google_section['credential'])
    SHEET_ID = google_section['sheetid']
    SERVICE_ACCOUNT_KEY = google_section['serviceaccountkey']

    # Measurements section
    measurements_section = config_section_map("measurements")

    METRIC_VALUES = check_metric_values(measurements_section['metricvalues'])

    # Log section
    log_section = config_section_map("log")

    LOG_LEVEL = check_log_level(log_section['loglevel'])

    # Backlog section
    backlog_section = config_section_map("backlog")

    BACKLOG_AUTH = backlog_section['user'], backlog_section['password']

    # Github section
    github_section = config_section_map("github")

    GITHUB_TOKEN = github_section['token']

    # Jira section
    jira_section = config_section_map("jira")

    JIRA_DOMAIN = jira_section['domain']
    JIRA_USERNAME = jira_section['username']
    JIRA_PASSWORD = jira_section['password']

    # Docker section
    docker_section = config_section_map("docker")

    DOCKER_ORGANIZATION = docker_section['organization']
    DOCKER_USERNAME = docker_section['username']
    DOCKER_PASSWORD = docker_section['password']
else:
    msg = '\nERROR: There is not defined TSC_DASHBOARD_SETTINGS_FILE environment variable ' \
          '\n       pointing to configuration file or there is no tsc-dashboard.ini file' \
          '\n       in the /etd/init.d directory.' \
          '\n\n       Please correct at least one of them to execute the program.'
    exit(msg)

# Settings file is inside Basics directory, therefore I have to go back to the parent directory
# to have the Code Home directory
CODE_HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_HOME = os.path.join(CODE_HOME, 'logs')
SERVICE_ACCOUNT_KEY_HOME = os.path.join(CODE_HOME, 'config')
