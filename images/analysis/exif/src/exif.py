import json

from machina.core.worker import Worker

import exifread

class Exif(Worker):
    types = ['png', 'jpeg']

    def __init__(self, *args, **kwargs):
        super(Exif, self).__init__(*args, **kwargs)

    def callback(self, data, properties):
        # self.logger.info(data)
        data = json.loads(data)

        # resolve path
        target = self.get_binary_path(data['ts'], data['hashes']['md5'])
        self.logger.info("resolved path: {}".format(target))

        with open(target, 'rb') as f:
            exif_tags = exifread.process_file(f)

        self.logger.info(exif_tags)

        # Convert all values to strings
        tags = {}
        for t in exif_tags.keys():
            tags[t] = str(exif_tags[t])

        png = self.graph.get_vertex(data['id'])
        png.exif = tags
        png.save()