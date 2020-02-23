import json
import string

from ioc_finder import find_iocs

from machina.core.worker import Worker
from machina.core.models.relationships.extracts import Extracts

def _strings(data, min=4):
    result = ""
    for c in data:
        if c in string.printable:
            result += c
            continue
        if len(result) >= min:
            yield result
        result = ""
    if len(result) >= min:  # catch result at EOF
        yield result

class FindURLs(Worker):
    types = ['*']
    
    def __init__(self, *args, **kwargs):
        super(FindURLs, self).__init__(*args, **kwargs)

    def callback(self, data, properties):
        # self.logger.info(data)
        data = json.loads(data)

        # resolve path
        target = self.get_binary_path(data['ts'], data['hashes']['md5'])
        self.logger.info("hello resolved path: {}".format(target))

        with open(target, 'r', errors="ignore") as f:
            strings = ' '.join(_strings(f.read()))

        urls = find_iocs(strings)['urls']

        self.logger.info("found urls: {}".format(urls))

        # Resolve origin node
        origin_node = self.graph.get_vertex(data['id'])

        # For each URL, create a node for it
        # And link it back to the original node
        for url in urls:
            self.logger.info("creating url node for: {}".format(url))
            url_node = self.graph.urls.create(url=url)
            self.logger.info("creating link")
            self.graph.create_edge(Extracts, origin_node, url_node)

