from datetime import datetime
import json

import ssdeep

from machina.core.worker import Worker

class SSDeepAnalysis(Worker):
    types = ['*']
    next_queues = ['SimilarityAnalysis']

    def __init__(self, *args, **kwargs):
        super(SSDeepAnalysis, self).__init__(*args, **kwargs)

    def callback(self, data, properties):
        # self.logger.info(data)
        data = json.loads(data)

        # resolve path
        target = self.get_binary_path(data['ts'], data['hashes']['md5'])
        self.logger.info("resolved path: {}".format(target))

        # Compute SSDeep Hash
        with open(target, 'rb') as f:
            ssdeep_hash = ssdeep.hash(f.read())

        self.logger.info("ssdeep for {} is {}".format(target, ssdeep_hash))

        # Update node
        updates = dict(ssdeep=ssdeep_hash)
        self.update_node(data['id'], updates)

        body = json.dumps({
            'ts': datetime.now().strftime("%Y%m%d%H%M%S%f"),
            'id': data['id'],
            'hashes': data['hashes']
        })

        # Publishes direct to next_queues
        self.publish_next(body)