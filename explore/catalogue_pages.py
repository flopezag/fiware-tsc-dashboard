import pprint
from datetime import date
from dbase import db, Source
from kernel.ganalytics import ga
from kernel.google import get_service

__author__ = 'Manuel Escriche'

source = db.query(Source).filter_by(name='Catalogue').one()
view = ga().search_view(source.url)
service = get_service('analyticsreporting')
body = {'reportRequests': [{'viewId': view['profile_id'],
                            'dateRanges': [{
                                 "startDate": "2015-09-01",
                                 "endDate": date.today().strftime('%Y-%m-%d')
                            }],
                            'metrics': [{'expression': 'ga:pageviews'}],
                            'dimensions': [{'name': 'ga:PagePath'}],
                            "dimensionFilterClauses": [{
                                 "filters": [{
                                     "dimensionName": "ga:PagePath",
                                     "operator": "BEGINS_WITH",
                                     "expressions": "/enablers/"
                                 }]
                            }],
                            # "orderBys":[{"fieldName": "ga:pageviews", "sortOrder": "DESCENDING"}]
                            }],
        }

try:
    data = service.reports().batchGet(body=body).execute()
except:
    raise

pages = [row['dimensions'][0] for row in data['reports'][0]['data']['rows']]
pprint.pprint(pages)
