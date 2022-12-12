import base64
import gzip
import json

from machina.core.worker import Worker


class Gz(Worker):
    types = ['gzip']

    def __init__(self, *args, **kwargs):
        super(Gz, self).__init__(*args, **kwargs)

    def callback(self, data, properties):
        # self.logger.info(data)
        data = json.loads(data)

        # resolve path
        target = self.get_binary_path(data['ts'], data['hashes']['md5'])
        self.logger.info(f"resolved path: {target}")

        with gzip.open(target, 'rb') as f:
            data_encoded = base64.b64encode(f.read()).decode()
            body = {
                    "data": data_encoded,
                    "origin": {
                        "ts": data['ts'],
                        "md5": data['hashes']['md5'],
                        "id": data['id'], #I think this is the only field needed, we can grab the unique node based on id alone
                        "type": data['type']}
                    }

        channel = self.get_channel(self.config['rabbitmq'])
        channel.basic_publish(exchange='machina',
            routing_key='Identifier',
            body=json.dumps(body))
