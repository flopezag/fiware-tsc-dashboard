import re
import requests
import json
from dbase import db, Source

__author__ = 'Manuel Escriche'

source = db.query(Source).filter_by(name='Coverall').one()
keyword = 'Wirecloud/wirecloud'
url = 'https://{}/github/{}'.format(source.url, keyword)
# print(url)
pattern = re.compile(r'\<.*?id=\'repoShowPercentage\'\>(.*?)\<.*?\>', re.DOTALL)
answer = requests.get(url, params={'branch': 'HEAD'})
print(answer.url)

if not answer.ok:
    raise Exception

match = re.search(pattern, answer.text)

if match:
    print(match.group(1).strip())
else:
    print('not match')

#print(answer.text)
