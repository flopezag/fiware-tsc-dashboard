from github import Github
import pprint

__author__ = 'Manuel Escriche'

gh = Github('adc842f790105942e095f5f77484ffa8242a2ec3')
repo = gh.get_user('mmilidoni').get_repo("github-downloads-count")
releases = repo.get_releases()
download_count = n_assets = 0
for rel in releases:
    assets = rel._rawData['assets']
    for asset in assets:
        n_assets += 1
        download_count += asset['download_count']

print('#assets={}, #downloads={}'.format(n_assets, download_count))
