import requests
import json
import datetime
import time


class AskBot:
    def __init__(self, domain='ask.fiware.org'):
        self.name = 'Askbot'
        self.questions_url = 'https://' + domain + '/api/v1/questions/'
        self.questions = list()

    def get_questions(self):
        page = 1
        params = {'scope': 'all', 'sort': 'age-asc', 'page': page}

        indata = requests.get(self.questions_url, params=params)
        indata = json.loads(indata.text)
        total_pages = int(indata['pages'])
        self.questions += indata['questions']

        page = page + 1

        while page <= total_pages:
            params['page'] = page

            indata = requests.get(self.questions_url, params=params)
            indata = json.loads(indata.text)
            total_pages = int(indata['pages'])
            self.questions += indata['questions']

            page += 1

    def filter_questions(self):
        start = datetime.date(2019, 3, 7)  # year, month, day
        end = datetime.date(2019, 7, 16)  # year, month, day

        start = int(time.mktime(start.timetuple()))
        end = int(time.mktime(end.timetuple()))

        result = list(filter(lambda x: start < int(x['added_at']) < end, self.questions))
        result = list(map(lambda x: self.get_values(x), result))

        return result

    def get_values(self, data):
        # Need to get View Counts, Answers Counts, Added At, Last Activity At
        result = dict()

        # Date/Time format: 04.02.2019  15:24:14

        result['answer_count'] = data['answer_count']
        result['view_count'] = data['view_count']
        result['last_activity_at'] = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(int(data['last_activity_at'])))
        result['added_at'] = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(int(data['added_at'])))

        return result

    def print_values(self, data):
        list(map(lambda x: print('{}\t{}\t"{}"\t"{}"'.format(x['answer_count'], x['view_count'], x['last_activity_at'], x['added_at'])), data))


if __name__ == "__main__":
    a = AskBot()

    a.get_questions()
    filtered_result = a.filter_questions()
    a.print_values(filtered_result)
