import requests
from config.settings import BACKLOG_AUTH

__author__ = 'Manuel Escriche'


class UnknownEnabler(Exception):
    pass


class InvalidConection(Exception):
    pass


class ScrumServer:
    def __init__(self, url):
        url = url or 'backlog.fiware.org'
        self.url = 'http://{}'.format(url)
        # self.url = 'http://127.0.0.1:5000'

    def getbacklog(self, enablername):
        url = self.url + '/api/backlog/enabler/' + enablername
        answer = requests.get(url, auth=BACKLOG_AUTH)

        if not answer.ok:
            raise InvalidConection

        return answer.json()

    def gethelpdesk(self, enablername):
        url = self.url + '/api/helpdesk/enabler/' + enablername
        answer = requests.get(url, auth=BACKLOG_AUTH)

        if not answer.ok:
            raise InvalidConection

        return answer.json()

    def getworkingmode(self):
        url = self.url + '/api/enabler/working_mode'
        answer = requests.get(url, auth=BACKLOG_AUTH)

        if not answer.ok:
            raise InvalidConection

        return answer.json()
