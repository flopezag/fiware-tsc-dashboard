#!/usr/bin/env bash
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



# Initializing variables

PYTHON_FILE="dashboard.py"
INITIAL_HEADER="#\!\/usr\/bin\/env python"
FINAL_HEADER='#\!\/usr\/bin\/env '
VIRTUALENV_DIR='\/env\/bin\/python'



# 1) Install&Config virtualenv for DesksReminder
if [ ! -d "env" ]; then
  # Control will enter here if env does not exist.
  virtualenv -p python2.7 env

  source env/bin/activate
  pip install -r requirements.txt

  deactivate
fi



# 2) Configure dashboard.py file

working_directory=${PWD}

result=$(echo ${working_directory} | sed 's@/@\\/@g')

FINAL_HEADER=${FINAL_HEADER}${result}${VIRTUALENV_DIR}

sed -i -e "s/${INITIAL_HEADER}/${FINAL_HEADER}/" ${PYTHON_FILE}

chmod 744 ${PYTHON_FILE}



# 3) Configure logrotate

# Take the file and generate the proper content based on installation
PATH_TO_CHANGE='\/logs\/tsc-dashboard\.log'
NEW_PATH=${result}${PATH_TO_CHANGE}

sed -i -e "s/${PATH_TO_CHANGE}/${NEW_PATH}/" ./config/tsc-dashboard.logrotate

echo ""
echo ""
echo "Please, with root user, execute the following command:"
echo ""
echo "cp ./config/tsc-dashboard.logrotate /etc/logrotate.d/tsc-dashboard"



# 4) configure crontab
username=$(whoami)
result=$(crontab -u ${username} -l 2>/dev/null)

if [ "$result" == "" ]; then
    if [ -e /tmp/cronlock ]; then
        echo "cronjob locked"
        exit 1
    fi

    touch /tmp/cronlock

    echo "# FIWARE TSC Enabler Dashboard" | crontab -
    (crontab -l; echo "00 4 * * * "${working_directory}"/dashboard.py --noauth_local_webserver") | crontab -

    rm -f /tmp/cronlock

else
    crontab -u ${username} -l 2>/dev/null >a.out

    touch /tmp/cronlock

    line=$(grep "00 4 * * mon-fri "${working_directory}"/dashboard.py --noauth_local_webserver" a.out)
    if [ "$line" == "" ]; then
        (crontab -l; echo "") | crontab -
        (crontab -l; echo "# FIWARE TSC Enabler Dashboard") | crontab -
        (crontab -l; echo "00 4 * * * "${working_directory}"/dashboard.py --noauth_local_webserver") | crontab -
    fi

    rm -f /tmp/cronlock

    rm a.out
fi
