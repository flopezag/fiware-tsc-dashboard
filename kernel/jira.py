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
import base64
import requests
from config.settings import JIRA_DOMAIN, JIRA_PASSWORD, JIRA_USERNAME
from config import enablers, endpoints
from dateutil import parser
import pytz
import datetime
from functools import reduce

__author__ = 'Fernando Lopez'


class ConnectionToJIRA(Exception):
    pass


class Jira:

    def __init__(self):
        self.fields = 'summary,status,project,components,priority,issuetype,description,reporter,' \
                 'resolution,assignee,created,updated,duedate,resolutiondate,fixVersions,releaseDate,issuelinks,' \
                 'customfield_11103,customfield_11104,customfield_11105'

        aux = list(map(lambda x: dict([(x['name'], x['chapter'])]), enablers))
        aux = reduce(lambda a, b: dict(a, **b), aux)
        aux = list(map(lambda x: dict([(x['helpdesk'], aux[x['enabler']])]), endpoints))
        self.enablers = reduce(lambda a, b: dict(a, **b), aux)

        self.verify = False

        self.url_api = {
            'project': '/rest/api/latest/project',
            'component': '/rest/api/latest/component/',
            'search': '/rest/api/latest/search',
            'issue': '/rest/api/latest/issue'
        }

        auth = '{}:{}'.format(JIRA_USERNAME, JIRA_PASSWORD).encode("utf-8")
        keyword = base64.b64encode(auth)

        headers = {'Content-Type': 'application/json', "Authorization": "Basic {}".format(keyword.decode("utf-8"))}

        self.root_url = 'https://{}'.format(JIRA_DOMAIN)
        self.session = requests.session()

        try:
            answer = self.session.get(self.root_url, headers=headers, verify=self.verify)
        except ConnectionToJIRA:
            raise Exception

        if answer.status_code != requests.codes.ok:
            raise ConnectionToJIRA

        self.session.headers.update({'Content-Type': 'application/json'})

    def get_component_data(self, comp_id):
        jql = 'component = "{}" AND project = {} AND type = WorkItem AND summary !~ Agile'\
            .format(comp_id, self.enablers[comp_id])

        return self.get_data(jql)

        return data

    def get_helpdesk(self, comp_id):
        jql = 'project = HELP AND HD-Enabler = {}'\
            .format(comp_id)

        return self.get_data(jql)

    def get_data(self, jql):
        start_at = 0

        payload = {
            'fields': self.fields,
            'maxResults': 1000,
            'startAt': start_at,
            'jql': jql
        }

        try:
            data = self.search(payload)
        except Exception:
            raise Exception

        total_issues, received_issues = data['total'], len(data['issues'])

        while total_issues > received_issues:
            payload['startAt'] = received_issues

            try:
                data['issues'].extend(self.search(payload)['issues'])
            except Exception:
                raise Exception

            received_issues = len(data['issues'])

        return data['issues']

    def search(self, params):
        url = '{}{}'.format(self.root_url, self.url_api['search'])
        try:
            answer = self.session.get(url, params=params, verify=self.verify)
        except Exception:
            raise ConnectionToJIRA

        # print(answer.url)
        data = answer.json()
        return data

    def difference_time(self, a, b):
        t_now = pytz.utc.localize(datetime.datetime.utcnow())
        t_created = parser.parse(b)

        if a is None:
            t_resolved = t_now
        else:
            t_resolved = parser.parse(a)

        # Translate the different in seconds to days (60sec*60min*24h = 86400)
        time_resolve = (t_resolved - t_created).total_seconds() / 86400

        return time_resolve


if __name__ == "__main__":
    jira = Jira()

    result = jira.get_component_data('FogFlow')

    status = map(lambda x: x['fields']['status']['name'], result)

    total_workitems = len(status)
    closed_workitems = len(filter(lambda x: x == 'Closed', status))
    rest_workitems = total_workitems - closed_workitems

    print("Total WorkItems Not Closed: {}\nTotal WorkItems Closed: {}".format(rest_workitems, closed_workitems))

    result = jira.get_helpdesk('FogFlow')

    status = map(lambda x: x['fields']['status']['name'], result)

    total_tickets = len(status)
    closed_tickets = len(filter(lambda x: x == 'Closed', status))
    rest_tickets = total_tickets - closed_tickets
    pending_tickets = int(round(float(rest_tickets) / float(total_tickets) * 100))

    resolutionDates = map(lambda x: parser.parse(x['fields']['resolutiondate']), result)
    createdDates = map(lambda x: parser.parse(x['fields']['created']), result)
    diff = map(lambda x: jira.difference_time(x['fields']['resolutiondate'], x['fields']['created']), result)

    numberDays = reduce(lambda x,y: x+y, diff) / len(diff)
    numberDays = int(round(numberDays))

    print(pending_tickets)
    print(diff)
    print(numberDays)
