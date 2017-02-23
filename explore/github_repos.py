from github import Github
from dbase import db, Source
from config.settings import GITHUB_TOKEN

__author__ = 'Manuel Escriche'

source = db.query(Source).filter_by(name='GitHub').one()
gh = Github(login_or_token=GITHUB_TOKEN)

for metric in source.metrics:
    print('->', metric.enabler_imp.name)

    if not metric.details:
        print('{} metric not defined'.format(metric.enabler_imp.name))
        continue

    items = [metric.details] if isinstance(metric.details, str) else metric.details

    for item in items:
        user, project = item.split('/')
        # print(user, project)
        repo = gh.get_user(user).get_repo(project)
        print('-->', repo.name, repo.html_url, 'updated at {} - pushed at {}'.format(repo.updated_at, repo.pushed_at))
        releases = repo.get_releases()
        for release in releases:
            try:
                print("\t->", release, ' published at {}'.format(release.raw_data['published_at']))
            except:
                continue
