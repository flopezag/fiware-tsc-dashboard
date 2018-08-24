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
import re
import requests
import json
from datetime import date
from github import Github
from dbase import db, Source
from .google import get_service
from .ganalytics import ga
from .scrum import ScrumServer
from config.settings import GITHUB_TOKEN
import sys
from config.log import logger


reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

__author__ = 'Fernando López'

github_stats = list()


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

        rows = filter(lambda x: token in x['dimensions'][0], self.data['reports'][0]['data']['rows'])
        values = map((lambda x: int(x['metrics'][0]['values'][0])), rows)
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
        self.source = db.query(Source).filter_by(name='Helpdesk').one()
        self.scrm = ScrumServer(self.source.url)

    def get_measurement(self, metric):
        super(Helpdesk, self).get_measurement(metric)
        enablername = metric.details
        try:
            value = self.scrm.gethelpdesk(enablername)
        except:
            raise
        else:
            if value['stats']['n']:
                return '{:3,d} ({:2.0%}) | {:2.0f}'\
                    .format(value['stats']['n'], value['resolution_level'], value['stats']['mean'])
            else:
                return '{:3,d} (-%) | - '.format(value['stats']['n'])


class Docker(DataSource):
    def __init__(self):
        super(Docker, self).__init__()
        self.source = db.query(Source).filter_by(name='Docker').one()
        url = 'https://{}/u/fiware/'.format(self.source.url)
        pattern = re.compile(r'"name":"[\w\-\.]*".*?"pull_count":\d*')
        self.data = []
        for n in range(10):
            answer = requests.get(url, params={'page': n})

            if not answer.ok:
                continue

            for match in re.finditer(pattern, answer.text):
                self.data.append(json.loads('{' + match.group(0) + '}'))

    def get_measurement(self, metric):
        super(Docker, self).get_measurement(metric)
        pattern = eval("r'{}'".format(metric.details))
        records = filter(lambda x: re.search(pattern, x['name']), self.data)

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
        self.metric_id = 0

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
        n_assets = 0
        download_count = 0

        # Get the number of assets and downloads
        for rel in releases:
            assets = rel._rawData['assets']
            for asset in assets:
                n_assets += 1
                download_count += asset['download_count']

        # Obtain the number of issues opened and closed
        open_issues = repo.get_issues()
        total_issues = repo.get_issues(state='all')
        list_open_issues = list(open_issues)
        list_total_issues = list(total_issues)
        len_open_issues = len(list_open_issues)
        len_total_issues = len(list_total_issues)
        len_closed_issues = len_total_issues - len_open_issues

        # print('Total issues (Open/Closed): {} / {}'.format(len(list(open_issues)), closed_issues))

        # Obtain the total number of adopters (persons who create issues and they are not authors
        authors = [users.author.login for users in repo.get_stats_contributors()]
        reporter_issues = [users.user.login for users in total_issues]
        adopters = list(set(reporter_issues) - set(authors))
        len_adopters = len(adopters)

        # print("Total number of adopters: {}".format(len(adopters)))

        # Obtain number of issues opened and closed created by adopters
        open_issues_adopters = filter(lambda x: x.user.login in adopters, list_open_issues)
        total_issues_adopters = filter(lambda x: x.user.login in adopters, list_total_issues)
        len_open_issues_adopters = len(open_issues_adopters)
        len_total_issues_adopters = len(total_issues_adopters)
        len_closed_issues_adopters = len_total_issues_adopters - len_open_issues_adopters

        # print('Total issues by adopters (Open/Closed): {} / {}'
        # .format(len(list(open_issues_adopters)), closed_issues_adopters))

        # Obtain the number of commits only for gh-pages and default branch (usually master)
        commits = list()
        commits.append(len(list(repo.get_commits(sha=repo.default_branch))))

        try:
            commits.append(len(list(repo.get_commits(sha='gh-pages'))))
        except Exception as e:
            print(e)

        total_commits = sum([i for i in commits])

        # print("Total number of commits in default and gh-pages branches: {}".format(total_commits))
        logger.info("Project({}): open issues: {}, closed issues: {}, \n"
                    "adopters: {}, open issues adopters: {}, closed issues adopters: {}, \n"
                    "commits: {}".format(project,
                                         len_open_issues,
                                         len_closed_issues,
                                         len_adopters,
                                         len_open_issues_adopters,
                                         len_closed_issues_adopters,
                                         total_commits))

        stat = {
            'enabler_id': self.enabler_id,
            'open_issues': len_open_issues,
            'closed_issues': len_closed_issues,
            'adopters': len_adopters,
            'open_issues_adopters': len_open_issues_adopters,
            'closed_issues_adopters': len_closed_issues_adopters,
            'commits': total_commits
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
        return '{:4,d}'.format(value[0]['open_issues'])


class GitHub_Closed_Issues(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Closed_Issues, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)
        return '{:4,d}'.format(value[0]['closed_issues'])


class GitHub_Adopters(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Adopters, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)
        return '{:4,d}'.format(value[0]['adopters'])


class GitHub_Adopters_Open_Issues(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Adopters_Open_Issues, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)
        return '{:4,d}'.format(value[0]['open_issues_adopters'])


class GitHub_Adopters_Closed_Issues(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Adopters_Closed_Issues, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)
        return '{:4,d}'.format(value[0]['closed_issues_adopters'])


class GitHub_Commits(DataSource):
    global github_stats

    def __init__(self):
        super(GitHub_Commits, self).__init__()

    def get_measurement(self, metric):
        value = filter(lambda ge_metric: ge_metric['enabler_id'] == metric.enabler_id, github_stats)
        return '{:4,d}'.format(value[0]['commits'])
