from github import Github
from config.settings import GITHUB_TOKEN

__author__ = 'Fernando Lopez'

gh = Github(login_or_token=GITHUB_TOKEN)
repo = gh.get_user('telefonicaid').get_repo("fiware-orion")
releases = repo.get_releases()
download_count = n_assets = 0
for rel in releases:
    assets = rel.raw_data['assets']
    for asset in assets:
        n_assets += 1
        download_count += asset['download_count']

print('#assets={}, #downloads={}'.format(n_assets, download_count))

openIssues = repo.get_issues()
totalIssues = repo.get_issues(state='all')
closedIssues = len(list(totalIssues)) - len(list(openIssues))

print('Total issues (Open/Closed): {} / {}'.format(len(list(openIssues)), closedIssues))

# AUTHORS
authors = [users.author.login for users in repo.get_stats_contributors()]
reporterIssues = [users.user.login for users in totalIssues]
adopters = list(set(reporterIssues)-set(authors))

print("Total number of adopters: {}".format(len(adopters)))

# TOTAL NUMBER OF ISSUES ONLY FOR ADOPTERS
openIssuesAdopters = filter(lambda x: x.user.login in adopters, list(openIssues))
totalIssuesAdopters = filter(lambda x: x.user.login in adopters, list(totalIssues))
closedIssuesAdopters = len(totalIssuesAdopters) - len(openIssuesAdopters)

print('Total issues by adopters (Open/Closed): {} / {}'.format(len(list(openIssuesAdopters)), closedIssuesAdopters))

# COMMITS only for default branch and gh-pages
out = list()
out.append(len(list(repo.get_commits(sha=repo.default_branch))))

try:
    out.append(len(list(repo.get_commits(sha='gh-pages'))))
except Exception as e:
    print(e)

result = sum([i for i in out])

print("Total number of commits in default and gh-pages branches: {}".format(result))

print("Total forks: {}".format(repo.forks))
print("Total watchers: {}".format(repo.subscribers_count))
print("Total stars: {}".format(repo.watchers))
