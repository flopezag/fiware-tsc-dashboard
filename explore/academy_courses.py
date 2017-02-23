import pprint
from datetime import date
from dbase import db, Source
from kernel.ganalytics import ga
from kernel.google import get_service

__author__ = 'Manuel Escriche'

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
pprint.pprint(courses)
