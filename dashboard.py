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
import os

from datetime import datetime
from dbase import db, EnablerImp, Source, Metric, Measurement, Admin
from kernel.google import get_service
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from config.settings import SHEET_ID, METRIC_VALUES, GITHUB_TOKEN
from config.constants import DB_NAME, DB_FOLDER, FIXED_ROWS, INITIAL_ROW, FIXED_COLUMNS, INITIAL_COLUMN
from dbase.database import Database
from dbase.measurement_search import MeasurementData
from config.log import logger
from config import enablers
from github import Github

__author__ = 'Fernando López'


class Dashboard:
    def __init__(self):
        self.check_database()
        self.enablers = db.query(EnablerImp)
        self.sources = db.query(Source)

        self.service = get_service('sheets')

    def __save__(self, values):
        # for row in values: print(row)

        body = {'values': values}
        area = 'Main!A3:X100'

        self.service.spreadsheets().values().update(spreadsheetId=SHEET_ID,
                                                    range=area,
                                                    valueInputOption='USER_ENTERED',
                                                    body=body).execute()

    @staticmethod
    def check_database():
        database_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_FOLDER, DB_NAME)

        if os.path.isfile(database_filename) is False:
            my_db = Database()
            my_db.show_data()

    def cleanup(self):
        row = [' ']
        values = []

        final_row = len(enablers) + FIXED_ROWS

        for m in range(INITIAL_COLUMN, FIXED_COLUMNS):
            row.extend([' '])

        for n in range(INITIAL_ROW, final_row):
            values.append(row)

        self.__save__(values=values)

    @staticmethod
    def getdate():
        """
        Get the creation date of the file enablers-dashboard.db
        :return: the creation date of the file
        """
        created_time = db.query(Admin).one().date.strftime('%d %b %Y at %H:%m')

        return created_time

    def generate_data(self):
        values = list()
        values.append(['Report date:', datetime.now().strftime('%d %b %Y at %H:%m')])

        # Add the date in which the database schema was created last time
        values.append(['Data sources updated on:', self.getdate()])
        values.append(['', ''])
        header = ['Source']

        for source in self.sources:
            header.extend([source.name])

        values.append(header)
        units = ['Units']

        for source in self.sources:
            units.extend([source.units])

        values.append(units)
        values.append(['Enabler Implementation'])
        values.append(['', ''])

        for status in ('Incubated', 'Development', 'Support', 'Deprecated'):
            values.append([status.upper(), ''])
            for enabler in self.enablers:
                raw = []
                raw.extend([enabler.name])

                if status != enabler.status:
                    continue

                for source in self.sources:
                    try:
                        metric = db.query(Metric).filter_by(source_id=source.id, enabler_id=enabler.id).one()
                    except NoResultFound:
                        raw.extend(['Not defined'])
                        continue
                    else:
                        if not len(metric.measurements):
                            raw.extend(['No data'])
                            continue
                        measurement = db.query(Measurement)\
                            .filter_by(metric_id=metric.id)\
                            .order_by(desc(Measurement.date))\
                            .first()

                        raw.extend([measurement.value])
                values.append(raw)
            values.append([''])

        self.__save__(values=values)

    @staticmethod
    def get_number_access():
        gh = Github(login_or_token=GITHUB_TOKEN)

        rate_limiting = gh.rate_limiting
        rate_limiting_reset_time = gh.rate_limiting_resettime

        rate_limiting_reset_time = datetime.fromtimestamp(rate_limiting_reset_time)

        return rate_limiting, rate_limiting_reset_time


if __name__ == "__main__":
    logger.info("Initializing the script...")
    dashboard = Dashboard()

    logger.info("Cleaning the Google Excel file...")
    dashboard.cleanup()

    if METRIC_VALUES == 'update':
        logger.info("Starting process to get measurements...")
        measurements = MeasurementData()

        measurements.obtain()
        logger.info("Finished process to get measurements...")
    elif METRIC_VALUES == 'read':
        logger.info("Keeping data as it is in the DB...")

    logger.info("Updating the Google Excel file...")

    dashboard.generate_data()

    logger.info("Data analysis finished")

    rate_count, rate_count_reset_time = dashboard.get_number_access()
    logger.info("GitHub rate limiting at finish: {}".format(rate_count))
    logger.info("GitHub rate limiting reset time: {}".format(rate_count_reset_time))

    # TODO: Add footer to the Google sheet document.
