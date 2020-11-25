import collections
import json
import requests

Attribute = collections.namedtuple('Attribute', 'name type')
paper_attributes = [
    Attribute('title', 'text'),
    Attribute('author', 'text'),
    Attribute('doi', 'text'),
    Attribute('year', 'int'),
    Attribute('journal', 'text'),
    Attribute('abstract', 'text'),
    Attribute('body', 'text'),
    Attribute('auto_summary', 'text')
]


class PaperStore:

    def __init__(self, dataServiceUrl):
        self._dataServiceUrl = dataServiceUrl

    def get_all(self):
        response = requests.get(self._dataServiceUrl + '/papers')
        all_papers_json = response.text
        all_papers = json.loads(all_papers_json)

        return all_papers