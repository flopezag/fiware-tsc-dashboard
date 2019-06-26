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
from schema import Schema, Or, Use, And, SchemaError
from oauth2client.tools import argparser, run_flow
from config import enablers

__author__ = 'fla'


def process_arguments(params):
    """
    Process the received param to execute the corresponding code.

    :param params: The CLI arguments introduced by the user.
    :return: Nothing.
    """
    print(params)

    help = params['--help']
    dbupdate = params['--DBUpdate']
    flag = params['--noauth_local_webserver']
    version = params['--version']
    filter = params['--filter']
    publish = params['--publish']

    # TODO: Add help, version and DBUpdate operations
    if help:
        help_message()

    if version:
        version_message()

    if dbupdate:
        delete_db()

    return flag, filter, publish


def validate(params):
    """
    Validate the params that we receive from the CLI.

    :param params: List of params.
    :return: List of params validated or error.
    """
    s = Schema(
        {
            '--help': Or(True, False),
            '--version': Or(True, False),
            '--DBUpdate': Or(True, False),
            '--noauth_local_webserver': Or(True, False),
            '--publish': Or(True, False),
            '--filter': And(str, lambda s: len(s) > 3)
        }
    )

    try:
        params = s.validate(params)
    except SchemaError as e:
        message = "Error in the options specified"
        raise ValueError(message)

    return params


def delete_db():
    """
    It is required an update in the DB? if the answer is True, we delete the previous DB
    and the service will regenerate the DB, in case False, we do nothing. Default value
    is False.

    :return: Nothing.
    """

    # We have to delete the corresponding DB.
    # TODO

    print("TBD")


def help_message():
    # TODO

    print("TBD")


def version_message():
    # TODO

    print("TBD")