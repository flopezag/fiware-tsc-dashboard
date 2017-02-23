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
from dbase import db, EnablerImp, Source, Metric, Measurement
from kernel.google import get_service
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from config.settings import SHEET_ID, METRIC_VALUES
from config.constants import DB_NAME, DB_FOLDER
from dbase.database import Database
from dbase.measurement_search import MeasurementData
from config.log import logger

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
        for m in range(1, 24):
            row.extend([' '])

        for n in range(3, 67):
            values.append(row)

        self.__save__(values=values)

    def generate_data(self):
        values = list()
        values.append(['Report date:', datetime.now().strftime('%d %b %Y at %H:%m')])
        values.append(['', ''])
        header = ['Source']

        for source in self.sources:
            header.extend([source.name])

        values.append(header)
        units = ['Units']

        for source in self.sources:
            units.extend([source.units])

        values.append(units)
        values.append(['Enabler Impl'])
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


if __name__ == "__main__":
    logger.info("Initilaizing the script...")
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
