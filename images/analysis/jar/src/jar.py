import base64
import json
from zipfile import ZipFile

from machina.core.worker import Worker

class JarAnalyzer(Worker):
    types = ["jar"]

    def __init__(self, *args, **kwargs):
        super(JarAnalyzer, self).__init__(*args, **kwargs)

    def callback(self, data, properties):
        data = json.loads(data)

        # resolve path
        target = self.get_binary_path(data['ts'], data['hashes']['md5'])
        self.logger.info("resolved path: {}".format(target))
    
        zf = ZipFile(target)
        namelist = zf.namelist()

        # Retype as APK
        if 'classes.dex' in namelist and 'META-INF/MANIFEST.MF' in namelist:
            # retype (Submit original data to Identifier with origin metadata and 
            # new  type)
            self.logger.info("retyping {} to apk".format(target))
            with open(target, 'rb') as f:
                data_encoded = base64.b64encode(f.read()).decode()
            body = {
                    "data": data_encoded,
                    "origin": {
                        "ts": data['ts'],
                        "md5": data['hashes']['md5'],
                        "id": data['id'], #I think this is the only field needed, we can grab the unique node based on id alone
                        "type": data['type']},
                    'type': 'apk'}

            channel = self.get_channel(self.config['rabbitmq'])
            channel.basic_publish(exchange='machina',
                                    routing_key='Identifier',
                                    body=json.dumps(body))
        else:
            pass