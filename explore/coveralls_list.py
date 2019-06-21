import re
import requests
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
    value = match.group(1).strip().strip('%')
    value = float(value) / 100
    print('{:1.2f}'.format(value))
else:
    print('not match')

# print(answer.text)
