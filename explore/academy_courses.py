from datetime import date
from dbase import db, Source
from kernel.ganalytics import ga
from kernel.google import get_service
import re

__author__ = 'Manuel Escriche'

# Get the number of page views from the old academy platform
source = db.query(Source).filter_by(name='Academy').one()
view = ga().search_view(source.url)
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
                            # "orderBys":[{"fieldName": "ga:pageviews", "sortOrder": "DESCENDING"}]
                            }],
        }

try:
    data = service.reports().batchGet(body=body).execute()
except:
    raise

courses = [row['dimensions'][0] for row in data['reports'][0]['data']['rows']]
print(courses)

pattern = eval("r'{}'".format('Orion Context Broker'))

rows = filter(lambda x: re.search(pattern, x['dimensions'][0]), data['reports'][0]['data']['rows'])
values = map((lambda x: int(x['metrics'][0]['values'][0])), rows)
value = reduce((lambda x, y: x + y), values)

print(value)
