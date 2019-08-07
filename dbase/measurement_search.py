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
from datetime import datetime
from dbase import db, Source, Metric, Measurement
from kernel import Readthedocs, Backlog, Helpdesk, Catalogue, Academy, Docker, GitHub, Coverall, \
    GitHub_Open_Issues, GitHub_Closed_Issues, GitHub_Adopters, GitHub_Adopters_Open_Issues, \
    GitHub_Adopters_Closed_Issues, GitHub_Commits, GitHub_Forks, GitHub_Watchers, GitHub_Stars, \
    Jira_WorkItem_Not_Closed, Jira_WorkItem_Closed
from kernel.data_sources import NotImplemented, NotDefined
from kernel.scrum import InvalidConection
from config.log import logger

__author__ = 'Fernando López'


class MeasurementData:
    def __init__(self, flags, filter=None):
        self.flags = flags
        self.filter = filter
        pass

    def obtain(self):
        for source in db.query(Source):
            logger.info(source.name)

            metrics = db.query(Metric).filter_by(source_id=source.id).all()

            # If there is filter apply filter to the metrics
            if self.filter is not None:
                metrics = list(filter(lambda x: x.enabler_imp.name == self.filter, metrics))

            try:
                op_source = eval('{}(flags={})'.format(source.name, self.flags))
            except Exception as e:
                logger.error('source {} is not implemented'.format(source.name))
                logger.error(e)
                continue
            for metric in metrics:
                try:
                    value = op_source.get_measurement(metric)
                except NotDefined:
                    value = 'Not Defined'
                except NotImplemented:
                    value = 'No Impl'
                except InvalidConection:
                    value = 'No Connect'
                except Exception as e:
                    logger.error(e)
                    value = 'No Access'

                params = {'metric_id': metric.id, 'date': datetime.now(), 'value': value.replace(',', '')}

                logger.debug(params)

                measurement = Measurement(**params)
                db.add(measurement)
            else:
                db.commit()


if __name__ == "__main__":
    logger.info("Starting process to get measurements...")
    measurements = MeasurementData()

    measurements.obtain()
    logger.info("Finished process to get measurements...")
