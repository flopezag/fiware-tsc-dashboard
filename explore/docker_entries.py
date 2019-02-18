#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##
# Copyright 2019 FIWARE Foundation, e.V.
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
import requests
import json
from dbase import db, Source
import httplib

__author__ = 'Fernando López'


def print_data(item):
    print(item['name'], item['pull_count'])


source = db.query(Source).filter_by(name='Docker').one()

# 1st step: Retrieve a token from Docker Repository
url = 'https://{}/v2/users/login/'.format(source.url)

payload = {
    "username": "flopez",
    "password": "Docker04fla15"
}

headers = {"Content-type": "application/json"}

answer = requests.post(url, headers=headers, data=json.dumps(payload))

if answer.status_code == httplib.OK:
    token = answer.json()['token']
else:
    raise Exception('Error retrieving a token from Docker Registry.')

# 2nd step: Get list of repositories inside FIWARE organization
url = 'https://{}/v2/repositories/{}'.format(source.url, 'fiware')
authorization = 'JWT {}'.format(token)
header = {'Authorization': authorization}
param = {'page_size': 200}

answer = requests.get(url, headers=headers, params=param)

if answer.status_code == httplib.OK:
    data = answer.json()['results']

    map(lambda x: print_data(x), data)
else:
    raise Exception('Error getting information of the different repositories under FIWARE organization.')
