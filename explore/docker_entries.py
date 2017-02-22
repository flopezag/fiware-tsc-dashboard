import re
import requests
import json
from dbase import db, Source

__author__ = 'Manuel Escriche'

source = db.query(Source).filter_by(name='Docker').one()
url = 'https://{}/u/fiware/'.format(source.url)
pattern = re.compile(r'"name":"[\w\-\.]*".*?"pull_count":\d*')
data = []
for n in range(10):
    answer = requests.get(url, params={'page': n})

    if not answer.ok:
        continue

    for match in re.finditer(pattern, answer.text):
        data.append(json.loads('{' + match.group(0) + '}'))

for item in sorted(data, key=lambda x: x['name']):
    print(item['name'], item['pull_count'])
