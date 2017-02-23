import os
import pprint
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient import discovery
from config.settings import SERVICE_ACCOUNT_KEY

__author__ = 'Manuel Escriche'

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly',
          'https://www.googleapis.com/auth/spreadsheets']

home_dir = os.path.expanduser('~')
credential_dir = os.path.join(home_dir, '.credentials')

if not os.path.exists(credential_dir):
    raise Exception

credential_path = os.path.join(credential_dir, SERVICE_ACCOUNT_KEY)

try:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_path, scopes=SCOPES)
except ValueError:
    exit()
else:

    http_auth = credentials.authorize(Http())
    service = discovery.build('analytics', 'v3', http=http_auth)

    views = []
    accounts = service.management().accountSummaries().list().execute()

    for account in accounts.get('items'):
        account_id = account.get('id')
        properties = service.management().webproperties().list(accountId=account_id).execute()

        for my_property in properties.get('items'):
            property_id = my_property.get('id')
            profiles = service.management().profiles().list(accountId=account_id, webPropertyId=property_id).execute()

            for profile in profiles.get('items'):
                profile_id = profile.get('id')
                views.append({'account_id': account['id'],
                              'account_name': account['name'],
                              'property_id': my_property['id'],
                              'property_name': my_property['name'],
                              'website_url': my_property['websiteUrl'],
                              'profile_id': profile['id'],
                              'profile_name': profile['name']})

    # print(views)

    service = discovery.build('analyticsreporting', 'v4', http=http_auth)

    for view in views:
        pprint.pprint(view)
        body = {'reportRequests': [{'viewId': view['profile_id'],
                                    # 'dateRanges': [{
                                    #    'startDate': '7daysAgo',
                                    #    'endDate': 'today'}],
                                    'dateRanges': [],
                                    'metrics': [{'expression': 'ga:pageviews'}]
                                    }]
                }

        try:
            response = service.reports().batchGet(body=body).execute()
        except Exception as e:
            print(e)
        else:
            print(view)
            for report in response.get('reports', []):
                columnHeader = report.get('columnHeader', {})
                dimensionHeaders = columnHeader.get('dimensions', [])
                metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
                rows = report.get('data', {}).get('rows', [])

                for row in rows:
                    dimensions = row.get('dimensions', [])
                    dateRangeValues = row.get('metrics', [])

                    for header, dimension in zip(dimensionHeaders, dimensions):
                        print(header + ': ' + dimension)

                    for i, values in enumerate(dateRangeValues):
                        print('Date range (' + str(i) + ')')
                        for metricHeader, value in zip(metricHeaders, values.get('values')):
                            print(metricHeader.get('name') + ': ' + value)
