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
import time
import re

__author__ = 'fla'


class MonascaData:
    def __init__(self, data):
        self.timestamp = int(round(time.time() * 1000))

        self.dict_names = {
            'Coverall': 'ge.coveralls',
            'GitHub': ['ge.gh.assets.total', 'ge.gh.assets.downloads'],
            'GitHub_Adopters': 'ge.gh.adopters.total',
            'Academy': 'ge.pageviews.academy',
            'Helpdesk': ['ge.helpdesk.tickets', 'ge.helpdesk.pending', 'ge.helpdesk.days'],
            'Readthedocs': 'ge.pageviews.rtd',
            'GitHub_Adopters_Open_Issues': 'ge.gh.adopters.issues.open',
            'GitHub_Commits': 'ge.gh.commits',
            'GitHub_Open_Issues': 'ge.gh.issues.open',
            'Catalogue': 'ge.pageviews.catalogue',
            'GitHub_Forks': 'ge.gh.forks',
            'GitHub_Watchers': 'ge.gh.watchers',
            'GitHub_Adopters_Closed_Issues': 'ge.gh.adopters.issues.closed',
            'Docker': 'ge.docker.pulls',
            'GitHub_Stars': 'ge.gh.stars',
            'GitHub_Closed_Issues': 'ge.gh.issues.closed'
        }

        self.data = self.__extract_data__(data=data)

    @staticmethod
    def __extract_data__(data):
        def create_dict(key, value):
            aux = dict()

            aux[value[0]] = dict(zip(key[1:], value[1:]))

            return aux

        keys = data[3]
        values = [i for i in data[7:]
                  if i[0] not in ['INCUBATED', 'FULL', 'QUARANTINE', 'DEPRECATED', '']]

        result_list = list(map(lambda value: create_dict(key=keys, value=value), values))
        result_dict = dict((key, d[key]) for d in result_list for key in d)

        return result_dict

    def __get_measure__(self, metric, value, ge):
        measure = {
            "name": metric,
            "dimensions": {
                "ge": ge,
                "source": "fiware-tsc-dashboard"
            },
            "timestamp": self.timestamp,
            "value": value,
        }

        return measure

    @staticmethod
    def __get_int__(value):
        try:
            aux = int(value)
        except ValueError:
            aux = 0

        return aux

    def generate_payload(self):
        aux = list()
        for k1, v1 in self.data.items():
            for k2, v2 in v1.items():

                if v2.lower() not in ['not defined', 'no impl', 'no connect', 'no access', 'no data']:
                    if k2.lower() not in ['github', 'helpdesk']:
                        v2 = int(v2)

                        try:
                            k2 = self.dict_names[k2]

                            measure = self.__get_measure__(metric=k2, value=v2, ge=str(k1))

                            aux.append(measure)
                        except KeyError:
                            pass

                    else:  # It corresponds to the github or helpdesk case, multiple values
                        k2 = self.dict_names[k2]

                        if k2[0] is 'ge.helpdesk.tickets':
                            # It is expected 3 values associated to HelpDesk, format:  '12 (8%) | 24',   '0 (-%) | -'
                            regular_expression = r'[ ]*([0-9]*)[ ]*\(([0-9]*|.)%\)[ ]*[|][ ]*([0-9]*|.)$'
                            p = re.compile(regular_expression)
                            m = p.match(v2)

                            number_tickets = self.__get_int__(m.group(1))
                            percentage_open = self.__get_int__(m.group(2))
                            number_days = self.__get_int__(m.group(3))

                            measure = self.__get_measure__(metric=k2[0], value=number_tickets, ge=str(k1))
                            aux.append(measure)

                            measure = self.__get_measure__(metric=k2[1], value=percentage_open, ge=str(k1))
                            aux.append(measure)

                            measure = self.__get_measure__(metric=k2[2], value=number_days, ge=str(k1))
                            aux.append(measure)
                        elif k2[0] is 'ge.gh.assets.total':
                            # It is expected 2 values associated to Github Assets, format: ' 4 |   219'.  '0 |     0'
                            regular_expression = r'[ ]*([0-9]*)[ ]*[|][ ]*([0-9]*)$'
                            p = re.compile(regular_expression)
                            m = p.match(v2)

                            number_assets = self.__get_int__(m.group(1))
                            assets_downloads = self.__get_int__(m.group(2))

                            measure = self.__get_measure__(metric=k2[0], value=number_assets, ge=str(k1))
                            aux.append(measure)

                            measure = self.__get_measure__(metric=k2[1], value=assets_downloads, ge=str(k1))
                            aux.append(measure)

        return aux


if __name__ == "__main__":
    content = [
        ['Report date:', '04 Apr 2019 at 16:04'],
        ['Data sources updated on:', '04 Apr 2019 at 15:04'],
        ['', ''],
        [
            'Source',
            u'Catalogue',
            u'Academy',
            u'Readthedocs',
            u'Docker',
            u'GitHub',
            u'GitHub_Open_Issues',
            u'GitHub_Closed_Issues',
            u'GitHub_Adopters',
            u'GitHub_Adopters_Open_Issues',
            u'GitHub_Adopters_Closed_Issues',
            u'GitHub_Commits',
            u'Coverall',
            u'Helpdesk',
            u'Backlog',
            u'GitHub_Forks',
            u'GitHub_Watchers',
            u'GitHub_Stars',
            u'Jira_WorkItem_Not_Closed',
            u'Jira_WorkItem_Closed'
        ],
        [
            'Units',
            u'#pageviews',
            u'#pageviews',
            u'#pageviews',
            u'#pulls',
            u'#assets|#downloads',
            u'#issues',
            u'#issues',
            u'#adopters',
            u'#issues',
            u'#issues',
            u'#commits',
            u'%sourcecode',
            u'#tickets(%pend)|#days',
            u'#features|#stories|#bugs',
            u'#forks',
            u'#watchers',
            u'#stars',
            u'#workitems',
            u'#workitems'
        ],
        ['Enabler Implementation'],
        ['', ''],
        ['INCUBATED', ''],
        [u'OpenMTC', u' 1050', u'Not Defined', u'Not Defined', u'Not Defined', u' 0 |     0', u'  12', u'  24', u'  10',
         u'   3', u'  14', u' 115', u'Not Defined', u'12 (8%) | 24', u'Not Defined', u'  13', u'  15', u'  26', u'   0',
         u'   0'],
        [u'Orion-LD', u'Not Defined', u'Not Defined', u'Not Defined', u' 141', u' 0 |     0', u'  23', u'  19', u'   0',
         u'   0', u'   0', u'13457', 'Not defined', u'0 (-%) | -', u'Not Defined', u'   0', u'   7', u'   0',
         u'No Access', u'No Access'],
        [''],
        ['DEVELOPMENT', ''],
        [''],
        ['SUPPORT', ''],
        [''],
        ['QUARANTINE', ''],
        [''],
        ['DEPRECATED', ''],
        ['']
    ]

    monascaData = MonascaData(data=content)
    result = monascaData.generate_payload()
    print(result)
