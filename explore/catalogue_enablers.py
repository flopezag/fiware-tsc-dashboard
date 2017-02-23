import re
import requests
import json
from dbase import db, Source

__author__ = 'Manuel Escriche'

source = db.query(Source).filter_by(name='Catalogue').one()
url = 'https://{}/enablers/'.format(source.url)
'''<h2><a href="/enablers/authorization-pdp-authzforce">Authorization PDP - AuthZForce</a></h2>'''
pattern = re.compile(r'\<.*?href="/enablers/(.*?)"\>(.*?)\<.*?h2\>', re.DOTALL)
data = []

for n in range(10):
    answer = requests.get(url)
    print(answer.url)
    # print(answer.text)
    for match in re.finditer(pattern, answer.text):
        print(match.group(1), match.group(2))

exit()

for n in range(10):
    answer = requests.get(url, params={'page': n})

    if not answer.ok:
        continue

    for match in re.finditer(pattern, answer.text):
        data.append(json.loads('{' + match.group(0) + '}'))

for item in sorted(data, key=lambda x: x['name']):
    print(item['name'], item['pull_count'])
