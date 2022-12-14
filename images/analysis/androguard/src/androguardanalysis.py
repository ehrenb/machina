import base64
import json
import logging
import re

from androguard.misc import AnalyzeAPK

from machina.core.worker import Worker

class AndroguardAnalysis(Worker):
    types = ['apk']
    next_queues = ['Identifier']
    
    def __init__(self, *args, **kwargs):
        super(AndroguardAnalysis, self).__init__(*args, **kwargs)

    def callback(self, data, properties):
        # self.logger.info(data)
        data = json.loads(data)

        # reduce androguard logging level
        logging.getLogger('androguard').setLevel(logging.ERROR)

        # resolve path
        target = self.get_binary_path(data['ts'], data['hashes']['md5'])
        self.logger.info(f"resolved path: {target}")

        a, d, dx = AnalyzeAPK(target)

        # Basic APK information
        package = a.get_package()
        name = a.get_app_name()
        androidversion_code = a.get_androidversion_code()
        androidversion_name = a.get_androidversion_name()
        permissions = a.get_permissions()
        activities = a.get_activities()
        providers = a.get_providers()
        receivers = a.get_receivers()
        services = a.get_services()
        min_sdk_version = a.get_min_sdk_version()
        max_sdk_version = a.get_max_sdk_version()
        effective_target_sdk_version = a.get_effective_target_sdk_version()
        libraries = a.get_libraries()
        main_activity = a.get_main_activity()
        content_provider_uris = list()

        # Classes
        classes = [{'name': c.name,
                    'external': c.is_external(),
                    'api': c.is_android_api()} for c in dx.get_classes()]

        # Content providers URIs
        content_uris_regexs = self.config['worker']['content_uris_regexs']

        strings = []
        for dex in d:
            strings.extend(dex.get_strings())
        for s in strings:
            for r in content_uris_regexs:
                match = re.search(r, s, re.IGNORECASE)
                if match:
                    content_uri = match.group(0)
                    content_provider_uris.append(content_uri)
        # Dedupe
        content_provider_uris = list(set(content_provider_uris))

        updates = dict(
            name=name,
            package=package,
            androidversion_code=androidversion_code,
            androidversion_name=androidversion_name,
            permissions=permissions,
            activities=activities,
            providers=providers,
            receivers=receivers,
            services=services,
            min_sdk_version=min_sdk_version,
            max_sdk_version=max_sdk_version,
            effective_target_sdk_version=effective_target_sdk_version,
            libraries=libraries,
            main_activity=main_activity,
            classes=classes,
            content_provider_uris=content_provider_uris,
        )

        self.update_node(data['id'], updates)

        # Files
        files = a.get_files()

        # Send each internal file to Identifier for analysis
        for f in files:
            fdata = a.get_file(f)
            data_encoded = base64.b64encode(fdata).decode()
            body = json.dumps({
                    "data": data_encoded,
                    "origin": {
                        "ts": data['ts'],
                        "md5": data['hashes']['md5'],
                        "id": data['id'], #I think this is the only field needed, we can grab the unique node based on id alone
                        "type": data['type']}
                    })

            # channel = self.get_channel(self.config['rabbitmq'])
            # channel.basic_publish(exchange='machina',
            #                            routing_key='Identifier',
            #                            body=json.dumps(body))
            self.publish_next(body)