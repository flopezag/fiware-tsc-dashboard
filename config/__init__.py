import os
import json

__author__ = 'Manuel Escriche'

home = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(home, 'entities.json')) as file:
    entities = json.load(file)

with open(os.path.join(home, 'owners.json')) as file:
    owners = json.load(file)

with open(os.path.join(home, 'sources.json')) as file:
    sources = json.load(file)

with open(os.path.join(home, 'enablers.json')) as file:
    enablers = json.load(file)

with open(os.path.join(home, 'metrics_endpoints.json')) as file:
    endpoints = json.load(file)

# Extend the endpoints to add references to other GitHub and Jira metrics
new_list = list()
for endpoint in endpoints:
    # Expand Jira endpoints
    endpoint['jira_workitem_not_closed'] = endpoint['jira_workitem']
    endpoint['jira_workitem_closed'] = endpoint['jira_workitem']
    del endpoint['jira_workitem']

    # expand Github endpoints
    endpoint['github_open_issues'] = endpoint['github']
    endpoint['github_closed_issues'] = endpoint['github']
    endpoint['github_adopters'] = endpoint['github']
    endpoint['github_adopters_open_issues'] = endpoint['github']
    endpoint['github_adopters_closed_issues'] = endpoint['github']
    endpoint['github_commits'] = endpoint['github']
    endpoint['github_forks'] = endpoint['github']
    endpoint['github_watchers'] = endpoint['github']
    endpoint['github_stars'] = endpoint['github']

    new_list.append(endpoint)

endpoints = new_list
