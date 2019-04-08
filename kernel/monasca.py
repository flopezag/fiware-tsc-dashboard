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
import sys
from config.settings import OS_MONASCA_URL
from config.log import logger
from keystone import Keystone
from monasca_data import Monasca_Data


__author__ = 'fla'


class Monasca:
    def __init__(self, x_auth_token):
        self.url = OS_MONASCA_URL + '/v2.0/metrics'

        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-Auth-Token': x_auth_token}

    def send_measurements(self, measurements):
        logger.info('Sending measurements to Monasca...')

        monasca_data = Monasca_Data(data=measurements)
        measurements = monasca_data.generate_payload()

        logger.debug('Payload: {}'.format(measurements))

        try:
            r = requests.post(self.url, json=measurements,
                              headers=self.headers)

            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logger.error("Http Error: {}".format(errh))
            sys.exit(1)
        except requests.exceptions.ConnectionError as errc:
            logger.error("Error Connecting: {}".format(errc))
            sys.exit(1)
        except requests.exceptions.Timeout as errt:
            logger.error("Timeout Error: {}".format(errt))
            sys.exit(1)
        except requests.exceptions.RequestException as err:
            logger.error("OOps: Something Else: {}".format(err))
            sys.exit(1)

        logger.info(
            'Measurements sent to Monasca, status code: {}'.format(r.status_code))


if __name__ == "__main__":
    keystone = Keystone()

    token = keystone.get_token()

    monasca = Monasca(x_auth_token=token)

    # monasca.send_measurements(solution_data)

    # print(solution_data)
