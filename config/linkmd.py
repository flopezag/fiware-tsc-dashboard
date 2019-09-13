import re
from requests import get


class LinkMD:
    def __init__(self):
        regex_submodule = r"^#{2}(\s*:new:\s*|\s*:seedling:\s*|\s*)([a-zA-Z 0-9]*)(\s*\(Incubated\)|\s*)$"
        regex_generic_enablers = r"\s*\|\s*(.*)\s*\|\s*(.*)\s*\|\s*(.*)\s*\|\s*(.*)\s*\|\s*(.*)\s*\|\s*"
        regex_extract_info = r"^\s*:[a-zA-Z]*:\s*([a-zA-Z ]*)\s*:\s*\*{2}([a-zA-Z]*)\*{2}\s*|.*\[(.*)\]\((.*)\).*$"  # r".*\[(.*)\]\((.*)\).*$"

        self.prog_submodule = re.compile(regex_submodule)  # r"submodule \"(.*)\/(.*)\"")
        self.prog_generic_enablers = re.compile(regex_generic_enablers)
        self.prog_extract_info = re.compile(regex_extract_info)

        self.data = ''

    def markdown(self, url):
        self.data = get(url).text

    def __parser1__(self, text):
        ge = None
        matches = re.match(self.prog_submodule, text)

        if matches:
            matches[1]   # give me details is if it is incubated or not (new or seedling)
            ge = matches[2]

        return ge

    def __parser2__(self, text, branch):
        result = branch
        matches = re.match(self.prog_generic_enablers, text)

        if matches:
            for i in range(0, len(matches.groups())):
                info = re.match(self.prog_extract_info, matches[i])
                if info[1] is None:
                    print(info[3])
                    print(info[4])
                else:
                    print(info[1])
                    print(info[2])

            result = None

        return result

    def get_links(self):
        branch = None

        for line in self.data.splitlines():
            if branch == None:
                branch = self.__parser1__(line)

                if branch != None:
                    print("\n{}".format(branch))
            else:
                # I found a h2 title so now I have to check the links corresopnding to links
                # | :octocat: [Git Repository](https://github.com/telefonicaid/fiware-orion/) | :whale: [Docker Hub](https://hub.docker.com/r/fiware/orion/) | :books: [Documentation](https://fiware-orion.rtfd.io) | :mortar_board: [Academy](https://fiware-academy.readthedocs.io/en/latest/core/orion) | :dart: [Roadmap](https://github.com/telefonicaid/fiware-orion/blob/master/doc/roadmap.md) |
                branch = self.__parser2__(line, branch)


if __name__ == "__main__":
    md = LinkMD()

    # good md.markdown(url='https://raw.githubusercontent.com/FIWARE/catalogue/master/core/README.md')
    # good md.get_links()

    # good md.markdown(url='https://raw.githubusercontent.com/FIWARE/catalogue/master/data-publication/README.md')
    # good md.get_links()

    # peta falta Academy en OPC-UA y Sigfox -> md.markdown(url='https://raw.githubusercontent.com/FIWARE/catalogue/master/iot-agents/README.md')
    # peta falta Academy en OPC-UA y Sigfox -> md.get_links()

    # peta Cosmos tiene 2 books sin separador -> md.markdown(url='https://raw.githubusercontent.com/FIWARE/catalogue/master/processing/README.md')
    # peta Cosmos tiene 2 books sin separador -> md.get_links()

    # peta, Micro XRCE-DDS and FIROS has no academy -> md.markdown(url='https://raw.githubusercontent.com/FIWARE/catalogue/master/robotics/README.md')
    # peta, Micro XRCE-DDS and FIROS has no academy -> md.get_links()

    md.markdown(url='https://raw.githubusercontent.com/FIWARE/catalogue/master/security/README.md')
    md.get_links()

    # peta falta Roadmap en IoTAgent Node Lib -> md.markdown(url='https://raw.githubusercontent.com/FIWARE/catalogue/master/third-party/README.md')
    # peta falta Roadmap en IoTAgent Node Lib -> md.get_links()
