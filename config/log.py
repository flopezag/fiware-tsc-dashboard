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
from os.path import exists, join
from os import makedirs
from logging import getLogger, Formatter, FileHandler, StreamHandler, ERROR
from config.settings import LOG_HOME, LOG_LEVEL
from config.constants import LOG_FILE
from sys import stdout


if not exists(LOG_HOME):
    makedirs(LOG_HOME)

log_filename = join(LOG_HOME, LOG_FILE)
format_str = '%(asctime)s [%(levelname)s] %(module)s: %(message)s'
date_format = '%Y-%m-%dT%H:%M:%SZ'

logger = getLogger(__name__)
logger.setLevel(LOG_LEVEL)
formatter = Formatter(fmt=format_str, datefmt=date_format)

fh = FileHandler(filename=log_filename)
fh.setLevel(LOG_LEVEL)
fh.setFormatter(formatter)
logger.addHandler(fh)

sh = StreamHandler(stdout)
sh.setLevel(ERROR)
sh.setFormatter(formatter)
logger.addHandler(sh)
