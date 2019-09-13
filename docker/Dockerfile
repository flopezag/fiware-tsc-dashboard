FROM python:3.7-alpine

LABEL com.jira-management.version="1.3.0" \
      vendor="FIWARE Foundation, e.V." \
      com.jira-management.release-date="2019-08-20" \
      com.jira-management.version.is-production="yes" \
      com.jira-management.maintainer="Fernando López <fernando.lopez@fiware.org>"

# Install dependencies
RUN apk update && \
    apk add --no-cache git && \
    pip install --no-cache-dir -Iv sqlalchemy==1.3.3 && \
    pip install --no-cache-dir -Iv requests==2.21.0 && \
    pip install --no-cache-dir -Iv PyGithub==1.43.7 && \
    pip install --no-cache-dir -Iv oauth2client==4.1.3 && \
    pip install --no-cache-dir -Iv google-api-python-client==1.7.8 && \
    pip install --no-cache-dir -Iv configparser==3.7.4 && \
    pip install --no-cache-dir -Iv python-dateutil==2.8.0 && \
    pip install --no-cache-dir -Iv pytz==2019.1 && \
    pip install --no-cache-dir -Iv schema==0.7.0 && \
    pip install --no-cache-dir -Iv docopt==0.6.2

#     apk del gcc musl-dev libffi-dev openssl-dev python3-dev && \

# Define the default BRANCH to get the code
ARG BRANCH=master

# Create a group and user
RUN addgroup -S mgmt && adduser -S mgmt -G mgmt

# Define the working directory
WORKDIR /home/mgmt

# Get the python code of the service and uninstall git
RUN git clone -b $BRANCH https://github.com/flopezag/fiware-tsc-dashboard.git && \
    apk del git && \
    rm -f /var/cache/apk/* && \
    chown -R mgmt:mgmt fiware-tsc-dashboard/

# Tell docker that all future commands should run as the appuser user
USER mgmt

# Define the ENV variable
ENV TSC_DASHBOARD_SETTINGS_FILE /home/mgmt/fiware-tsc-dashboard/config/tsc-dashboard.ini

# Execute the service
CMD [ "python", "/home/mgmt/fiware-tsc-dashboard/dashboard.py", "-p --noauth_local_webserver" ]