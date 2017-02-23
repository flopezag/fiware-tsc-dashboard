from github import Github
from config.settings import GITHUB_TOKEN
import pprint

__author__ = 'Manuel Escriche'

gh = Github(login_or_token=GITHUB_TOKEN)
repo = gh.get_user('mmilidoni').get_repo("github-downloads-count")
releases = repo.get_releases()
download_count = n_assets = 0
for rel in releases:
    assets = rel._rawData['assets']
    for asset in assets:
        n_assets += 1
        download_count += asset['download_count']

print('#assets={}, #downloads={}'.format(n_assets, download_count))
