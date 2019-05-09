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
import operator
import re
import requests
import json
import sys
from datetime import date
from github import Github
from dbase import db, Source
from .google import get_service
from .ganalytics import ga
from .scrum import ScrumServer
from config.settings import GITHUB_TOKEN
from config.log import logger
from kernel.jira import Jira
from config.settings import DOCKER_USERNAME, DOCKER_PASSWORD
from dateutil import parser
from importlib import reload
from functools import reduce
from http import HTTPStatus

reload(sys)  # Reload does the trick!

__author__ = 'Fernando López'

github_stats = list()
jira_stats = list()


class NoViewFound(Exception):
    pass


class NotImplemented(Exception):
    pass


class InvalidKeyword(Exception):
    pass


class NoPageFound(Exception):
    pass


class NoValueFound(Exception):
    pass


class NotDefined(Exception):
    pass


class DataSource(object):
    def __init__(self):
        pass

    def get_measurement(self, metric):
        if not metric.details:
            raise NotDefined


class Readthedocs(DataSource):
    def __init__(self):
        super(Readthedocs, self).__init__()
        self.source = db.query(Source).filter_by(name='Readthedocs').one()
        self.ga = ga()

    def get_measurement(self, metric):
        super(Readthedocs, self).get_measurement(metric)
        token = metric.details if re.match(r'http://[\w+][\.\w+]+', metric.details) \
            else '{}.{}'.format(metric.details, self.source.url.split('.')[0])

        view = self.ga.search_view(token)

        if not view:
            raise NoViewFound

        service = get_service('analyticsreporting')
        body = {'reportRequests': [{'viewId': view['profile_id'],
                                    'dateRanges': [{
                                         "startDate": "2015-09-01",
                                         "endDate": date.today().strftime('%Y-%m-%d')
                                     }],
                                    'metrics': [{'expression': 'ga:pageviews'}]
                                    }]
                }

        try:
            response = service.reports().batchGet(body=body).execute()
        except:
            raise

        try:
            value = response['reports'][0]['data']['rows'][0]['metrics'][0]['values'][0]
        except:
            raise

        return '{:4,d}'.format(int(value))


class Catalogue(DataSource):
    """
    Class to return the pageviews of the different entries in the FIWARE Catalogue.
    Keep in mind that for each FIWARE Component is obtained all the pageviews from
    its base URL, for example the FIWARE GE application-mashup-wirecloud whose base
    URL is /enablers/application-mashup-wirecloud will obtain several measurements,
    each for the link below it:
      * /enablers/application-mashup-wirecloud
      * /enablers/application-mashup-wirecloud/documentation
      * /enablers/application-mashup-wirecloud/downloads
      * /enablers/application-mashup-wirecloud/creating-instances
      * /enablers/application-mashup-wirecloud/instances
      * /enablers/application-mashup-wirecloud/terms-and-conditions
      * ...

    We obtain the complete sum of all the pages.
    """

    def __init__(self):
        super(Catalogue, self).__init__()
        self.source = db.query(Source).filter_by(name='Catalogue').one()
        self.ga = ga()
        view = self.ga.search_view(self.source.url)
        service = get_service('analyticsreporting')
        body = {'reportRequests': [{'viewId': view['profile_id'],
                                    'dateRanges': [{
                                         "startDate": "2015-09-01",
                                         "endDate": date.today().strftime('%Y-%m-%d')
                                     }],
                                    'metrics': [{'expression': 'ga:pageviews'}],
                                    'dimensions': [{'name': 'ga:PagePath'}],
                                    "dimensionFilterClauses": [{
                                         "filters": [{
                                             "dimensionName": "ga:PagePath",
                                             "operator": "BEGINS_WITH",
                                             "expressions": "/enablers/"
                                         }]
                                    }],
                                    "orderBys": [{
                                         "fieldName": "ga:pageviews", "sortOrder": "DESCENDING"
                                    }]
                                    }],
                }

        try:
            self.data = service.reports().batchGet(body=body).execute()
        except:
            raise

        # pages = [row['dimensions'][0] for row in self.data['reports'][0]['data']['rows']]
        # pprint.pprint(pages)

    def get_measurement(self, metric):
        super(Catalogue, self).get_measurement(metric)
        token = metric.details

        rows = list(filter(lambda x: token in x['dimensions'][0], self.data['reports'][0]['data']['rows']))
        values = list(map((lambda x: int(x['metrics'][0]['values'][0])), rows))
        value = reduce((lambda x, y: x + y), values)

        return '{:6,d}'.format(value)


class Academy(DataSource):
    def __init__(self):
        super(Academy, self).__init__()
        self.source = db.query(Source).filter_by(name='Academy').one()
        self.ga = ga()
        view = self.ga.search_view(self.source.url)
        service = get_service('analyticsreporting')
        body = {'reportRequests': [{'viewId': view['profile_id'],
                                    'dateRanges': [{
                                         "startDate": "2015-09-01",
                                         "endDate": date.today().strftime('%Y-%m-%d')
                                    }],
                                    'metrics': [{'expression': 'ga:pageviews'}],
                                    'dimensions': [{'name': 'ga:pageTitle'}],
                                    "dimensionFilterClauses": [{
                                         "filters": [{
                                             "dimensionName": "ga:pageTitle",
                                             "operator": "BEGINS_WITH",
                                             "expressions": "Course"
                                         }]
                                    }],
                                    "orderBys": [{
                                         "fieldName": "ga:pageviews", "sortOrder": "DESCENDING"
                                    }]
                                    }],
                }

        try:
            self.data = service.reports().batchGet(body=body).execute()
        except:
            raise

        # courses = [row['dimensions'][0] for row in self.data['reports'][0]['data']['rows']]
        # pprint.pprint(courses)

    def get_measurement(self, metric):
        super(Academy, self).get_measurement(metric)
        pattern = eval("r'{}'".format(metric.details))

        rows = filter(lambda x: re.search(pattern, x['dimensions'][0]), self.data['reports'][0]['data']['rows'])
        values = map((lambda x: int(x['metrics'][0]['values'][0])), rows)
        value = reduce((lambda x, y: x + y), values)

        return '{:5,d}'.format(value)


class Backlog(DataSource):
    def __init__(self):
        super(Backlog, self).__init__()
        self.source = db.query(Source).filter_by(name='Backlog').one()
        self.scrm = ScrumServer(self.source.url)

    def get_measurement(self, metric):
        super(Backlog, self).get_measurement(metric)
        enablername = metric.details
        try:
            value = self.scrm.getbacklog(enablername)
        except:
            raise
        else:
            value = value['stats']
            return '{:2} | {:3} | {:3}'.format(value['Feature'], value['Story'], value['Bug'])


class Helpdesk(DataSource):
    def __init__(self):
        super(Helpdesk, self).__init__()
        self.jira = Jira()

    def get_measurement(self, metric):
        result = self.jira.get_helpdesk(metric.details)

        status = list(map(lambda x: x['fields']['status']['name'], result))

        total_tickets = len(status)
        closed_tickets = len(list(filter(lambda x: x == 'Closed', status)))
        rest_tickets = total_tickets - closed_tickets
        pending_tickets = int(round(float(rest_tickets) / float(total_tickets) * 100))

        resolutionDates = list(map(lambda x: parser.parse(x['fields']['resolutiondate']), result))
        createdDates = list(map(lambda x: parser.parse(x['fields']['created']), result))
        diff = list(map(lambda x: self.jira.difference_time(x['fields']['resolutiondate'], x['fields']['created']), result))

        numberDays = reduce(lambda x, y: x + y, diff) / len(diff)
        numberDays = int(round(numberDays))

        if total_tickets == 0:
            result = '0 (0%) | -'
        else:
            result = '{:3,d} ({:2.0%}) | {:2.0f}'.format(total_tickets, pending_tickets, numberDays)

        return result


class Docker(DataSource):
    def __init__(self):
        super(Docker, self).__init__()
        self.source = db.query(Source).filter_by(name='Docker').one()
        self.data = dict()

    def get_docker_hub_data(self, namespace):

        if namespace not in self.data:
            # 1st step: Retrieve a token from Docker Repository
            url = 'https://{}/v2/users/login/'.format(self.source.url)

            payload = {
                "username": DOCKER_USERNAME,
                "password": DOCKER_PASSWORD
            }

            headers = {"Content-type": "application/json"}

            answer = requests.post(url, headers=headers, data=json.dumps(payload))

            if answer.status_code == HTTPStatus.OK:
                token = answer.json()['token']
            else:
                raise Exception('Error retrieving a token from Docker Registry.')

            # 2nd step: Get list of repositories inside FIWARE organization
            url = 'https://{}/v2/repositories/{}'.format(self.source.url, namespace)
            authorization = 'JWT {}'.format(token)
            headers = {'Authorization': authorization}
            params = {'page_size': 200}

            answer = requests.get(url, headers=headers, params=params)

            if answer.status_code == HTTPStatus.OK:
                self.data[namespace] = answer.json()['results']
            else:
                raise Exception('Error getting information of the different repositories under FIWARE organization.')

            '''
            url = 'https://{}/u/fiware/'.format(self.source.url)
            pattern = re.compile(r'"name":"[\w\-\.]*".*?"pull_count":\d*')
            self.data = []
            for n in range(10):
                answer = requests.get(url, params={'page': n})
    
                if not answer.ok:
                    continue
    
                for match in re.finditer(pattern, answer.text):
                    self.data.append(json.loads('{' + match.group(0) + '}'))
            '''

    def get_measurement(self, metric):
        super(Docker, self).get_measurement(metric)

        keys = metric.details[0].split('/')

        if len(keys) == 1:
            # There is no namespace, therefore we confider fiware as a value
            # check if we have information from fiware docker repository and if
            # not get that information
            namespace = 'fiware'
            name = keys[0]

        elif len(keys) == 2:
            # We have the namespace and the name of the hub docker repository
            namespace, name = keys

        self.get_docker_hub_data(namespace)

        records = list(filter(lambda x: x['name'] == name and x['namespace'] == namespace, self.data[namespace]))

        value = 0
        values = [int(record['pull_count']) for record in records]

        value += sum(values)

        return '{:4,d}'.format(value)


class GitHub(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub, self).__init__()
        self.source = db.query(Source).filter_by(name='GitHub').one()
        self.gh = Github(login_or_token=GITHUB_TOKEN)
        self.enabler_id = 0

    def get_measurement(self, metric):
        super(GitHub, self).get_measurement(metric)
        self.enabler_id = metric.enabler_id
        items = [metric.details] if isinstance(metric.details, str) else metric.details
        download_count = n_assets = 0
        if isinstance(items, list):
            for item in items:
                user, project = item.split('/')

                assets, downloads = self.get_statistics(user, project)

                n_assets += assets
                download_count += downloads
        else:
            user, project = items.split('/')

            n_assets, download_count = self.get_statistics(user, project)

        return '{:2} | {:5,d}'.format(n_assets, download_count)

    def get_statistics(self, user, project):
        repo = self.gh.get_user(user).get_repo(project)
        releases = repo.get_releases()

        aux = list(filter(lambda x: len(x.raw_data['assets']) > 0, releases))
        assets = list(map(lambda x: x.raw_data['assets'][0]['download_count'], aux))

        n_assets = len(assets)

        if n_assets == 0:
            download_count = 0
        else:
            download_count = reduce(lambda x, y: x + y, assets)

        # Obtain the number of issues opened and closed
        total_issues = repo.get_issues(state='all')
        list_open_issues = list(map(lambda x: x.user.login, list(filter(lambda x: x.state == 'open', total_issues))))
        list_total_issues = list(map(lambda x: x.user.login, total_issues))
        len_open_issues = len(list_open_issues)
        len_total_issues = len(list_total_issues)
        len_closed_issues = len_total_issues - len_open_issues

        # Obtain the total number of adopters (persons who create issues and they are not authors
        # authors = [users.author.login for users in repo.get_stats_contributors()]
        list_authors = list(map(lambda x: x.author.login, repo.get_stats_contributors()))

        # Obtain the number of commits only for gh-pages and default branch (usually master)
        commits = list()
        commits.append(len(list(repo.get_commits(sha=repo.default_branch))))

        try:
            commits.append(len(list(repo.get_commits(sha='gh-pages'))))
        except Exception as e:
            url = 'https://github.com/{}/{}'.format(user, project)
            logger.warning('The project \'{}\'({}) has no \'gh-pages\' branch'.format(project, url))

        # total_commits = sum([i for i in commits])
        total_commits = reduce(lambda x, y: x + y, commits)

        logger.info("Project({}): open issues: {}, closed issues: {}, total issues: {}, authors: {}, commits: {}"
                    .format(project,
                            len_open_issues,
                            len_closed_issues,
                            len_total_issues,
                            len(list_authors),
                            total_commits))

        stat = {
            'enabler_id': self.enabler_id,
            'open_issues': list_open_issues,
            'total_issues': list_total_issues,
            'closed_issues': len_closed_issues,
            'authors': list_authors,
            'commits': total_commits,
            'forks': repo.forks,
            'watchers': repo.subscribers_count,
            'stars': repo.watchers
        }

        github_stats.append(stat)

        return n_assets, download_count


class Coverall(DataSource):
    def __init__(self):
        super(Coverall, self).__init__()
        self.source = db.query(Source).filter_by(name='Coverall').one()
        self.url = 'https://{}/github'.format(self.source.url)
        self.pattern = re.compile(r'\<.*?id=\'repoShowPercentage\'\>(.*?)\<.*?\>', re.DOTALL)

    def get_measurement(self, metric):
        super(Coverall, self).get_measurement(metric)
        url = '{}/{}'.format(self.url, metric.details)
        answer = requests.get(url, params={'branch': 'HEAD'})
        # print(answer.url)

        if not answer.ok:
            raise NoPageFound

        match = re.search(self.pattern, answer.text)

        if match:
            value = match.group(1).strip()
            return '{:2}'.format(value)
        else:
            raise NoValueFound


class GitHub_Open_Issues(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Open_Issues, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)

        open_issues = map(lambda x: x['open_issues'], value)
        total = len(reduce(operator.concat, open_issues))

        return '{:4,d}'.format(total)


class GitHub_Closed_Issues(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Closed_Issues, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)

        closed_issues = reduce(lambda x, y: x+y, map(lambda x: x['closed_issues'], value))

        return '{:4,d}'.format(closed_issues)


class GitHub_Adopters(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Adopters, self).__init__()

    def get_measurement(self, metric):
        value = list(filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats))

        authors = list(map(lambda x: x['authors'], value))
        authors = set(reduce(operator.concat, authors))

        total_issues = list(map(lambda x: x['total_issues'], value))
        total_reporter_issues = set(reduce(operator.concat, total_issues))

        adopters = len(list(total_reporter_issues - authors))

        return '{:4,d}'.format(adopters)


class GitHub_Adopters_Open_Issues(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Adopters_Open_Issues, self).__init__()

    def get_measurement(self, metric):
        value = list(filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats))

        authors = set(reduce(operator.concat, list(map(lambda x: x['authors'], value))))
        total_reporter_issues = set(reduce(operator.concat, list(map(lambda x: x['total_issues'], value))))

        adopters = list(total_reporter_issues - authors)

        open_issues = reduce(operator.concat, list(map(lambda x: x['open_issues'], value)))
        open_issues_adopters = len(list(filter(lambda x: x in adopters, open_issues)))

        return '{:4,d}'.format(open_issues_adopters)


class GitHub_Adopters_Closed_Issues(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Adopters_Closed_Issues, self).__init__()

    def get_measurement(self, metric):
        value = list(filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats))

        authors = set(reduce(operator.concat, list(map(lambda x: x['authors'], value))))
        total_reporter_issues = set(reduce(operator.concat, list(map(lambda x: x['total_issues'], value))))

        adopters = list(total_reporter_issues - authors)

        open_issues = reduce(operator.concat, list(map(lambda x: x['open_issues'], value)))
        open_issues_adopters = len(list(filter(lambda x: x in adopters, open_issues)))

        total_issues = reduce(operator.concat, list(map(lambda x: x['total_issues'], value)))
        total_issues_adopters = len(list(filter(lambda x: x in adopters, total_issues)))

        closed_issues_adopters = total_issues_adopters - open_issues_adopters

        return '{:4,d}'.format(closed_issues_adopters)


class GitHub_Commits(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Commits, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)

        commits = reduce(lambda x, y: x+y, map(lambda x: x['commits'], value))

        return '{:4,d}'.format(commits)


class GitHub_Forks(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Forks, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)

        forks = reduce(lambda x, y: x + y, map(lambda x: x['forks'], value))

        return '{:4,d}'.format(forks)


class GitHub_Watchers(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Watchers, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)

        watchers = reduce(lambda x, y: x + y, map(lambda x: x['watchers'], value))

        return '{:4,d}'.format(watchers)


class GitHub_Stars(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Stars, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)

        stars = reduce(lambda x, y: x + y, map(lambda x: x['stars'], value))

        return '{:4,d}'.format(stars)


class Jira_WorkItem_Not_Closed(DataSource):
    global jira_stats

    def __init__(self):
        super(Jira_WorkItem_Not_Closed, self).__init__()
        self.jira = Jira()

    def get_measurement(self, metric):
        result = self.jira.get_component_data(metric.details)

        status = map(lambda x: x['fields']['status']['name'], result)

        total_workitems = len(status)
        closed_workitems = len(filter(lambda x: x == 'Closed', status))
        rest_workitems = total_workitems - closed_workitems

        stat = {
            'enabler_id': metric.enabler_id,
            'not_closed_workitems': rest_workitems,
            'closed_workitems': closed_workitems,
        }

        jira_stats.append(stat)

        return '{:4,d}'.format(rest_workitems)


class Jira_WorkItem_Closed(DataSource):
    global jira_stats

    def __init__(self):
        super(Jira_WorkItem_Closed, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda x: x['enabler_id'] == metric.enabler_id, jira_stats)

        closed = reduce(lambda x, y: x + y, map(lambda x: x['closed_workitems'], value))

        return '{:4,d}'.format(closed)
