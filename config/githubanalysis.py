from os.path import join
from requests import get
import configparser
import re


# Analysis of the metrics_endpoint from fiware/catalogue

class GitHubAnalysis:
    def __init__(self, repo):
        basegithub = 'https://github.com/'
        baseraw = 'https://raw.githubusercontent.com'
        branch = 'master'
        modules = '.gitmodules'

        self.repo_raw_url = join(baseraw, repo)
        self.repo_raw_url = join(self.repo_raw_url, branch)
        self.repo_raw_url = join(self.repo_raw_url, modules)

        self.prog_submodule = re.compile(r"submodule \"(.*)\/(.*)\"")
        self.prog_multiple_repos = re.compile(r"(.*)\/(.*)")

    def __get_modules__(self):
        r = get(self.repo_raw_url)

        print(r)

        config = configparser.ConfigParser()
        config.read_string(r.text)

        sections = config.sections()
        ges = list()

        result = list(map(lambda x: {'chapter': self.__return_chapter__(x), 'ge': self.__return_ge__(), 'url': [config[x]['url']]}, sections))
        result = self.__filter_multiple_repos__(result)

        return result

    def __return_chapter__(self, original_data):
        # We have two options here:
        # - submodule "chapter/ge" -> url gives us the link to the repo (only one repo)
        # - submodule "chapter/ge/component -> url gives us the link to the repo (there are more than one repo)
        matches = re.match(self.prog_submodule, original_data)

        self.ge = matches[2]

        return matches[1]

    def __return_ge__(self):
        return self.ge

    def __filter_multiple_repos__(self, data):
        # We need to transform the dict to get url like a list of urls, if the chapter is unique we get only one url
        # if the chapter is 'chapter/ge' then we need to unify to a chapter, ge with several urls
        def clean(x):
            matches = re.match(self.prog_multiple_repos, x['chapter'])

            if matches:
                x['chapter'] = matches[1]
                x['ge'] = matches[2]

            return x

        result1 = list(map(lambda x: clean(x), data))

        result2 = list()
        for idx, item in enumerate(result1):
            # check if item['ge'] is inside result2[]['ge']
            new_ge = item['ge']
            ge_list2 = list(map(lambda x: x['ge'], result2))

            if new_ge in ge_list2:
                # Update elem in result2 and add the url of elem
                index = [index for index, value in enumerate(result2) if value['ge'] == item['ge']][0]
                result2[index]['url'].append(item['url'][0])
            else:
                result2.append(item)

        return result2


if __name__ == "__main__":
    githubData = GitHubAnalysis('FIWARE/catalogue')

    data = githubData.__get_modules__()

    print(data)

