"""this module expects that you have built the docker-emulator-android
images on your host (https://github.com/agoda-com/docker-emulator-android)"""

import json
import re
import time

from machina.core.worker import Worker

from androguard.core.bytecodes.apk import APK
import docker

class ContentURIAnalysis(Worker):
    types = ['apk']
    
    def __init__(self, *args, **kwargs):
        super(ContentURIAnalysis, self).__init__(*args, **kwargs)

    def callback(self, data, properties):
        # self.logger.info(data)
        data = json.loads(data)

        # resolve path
        target = self.get_binary_path(data['ts'], data['hashes']['md5'])
        self.logger.info("resolved path: {}".format(target))

        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        self.logger.info("client version: {}".format(client.version()))

        images = client.images.list("docker-registry-url/agoda/docker-emulator-android-*")
        self.logger.info("images: {}".format(images))

        # Map SDK version to the image name for easier lookup
        image_to_sdk = {}
        for i in images:
            tag = i.tags[0]
            result = re.search('docker-registry-url/agoda/docker-emulator-android-(\d*):latest', tag)
            version = result.group(1)

            image_to_sdk[version] = tag

        apk = self.graph.get_vertex(data['id'])

        # If none of the desired sdk data is available, run a minimal analysis using Androguard
        if not apk.min_sdk_version and not apk.max_sdk_version and not apk.effective_target_sdk_version:
            self.logger.info("SDK Version data not available yet, gathering it now...")
            a = APK(target)
            apk.min_sdk_version = a.get_min_sdk_version()
            apk.max_sdk_version = a.get_max_sdk_version()
            apk.effective_target_sdk_version = a.get_effective_target_sdk_version()
            apk.save()

        min_sdk_version = apk.min_sdk_version
        max_sdk_version = apk.max_sdk_version
        effective_target_sdk_version = apk.effective_target_sdk_version

        self.logger.info("min_sdk_version: {}".format(min_sdk_version))
        self.logger.info("max_sdk_version: {}".format(max_sdk_version))
        self.logger.info("effective_target_sdk_version: {}".format(effective_target_sdk_version))

        # Find the optimal target avd sdk version
        optimal_tag = None

        # If effective SDK match, prefer that
        if effective_target_sdk_version:
            for version, tag in image_to_sdk.items():
                if int(effective_target_sdk_version) == int(version):
                    optimal_tag = tag
                    break
        else:
            candidate_tags = {}
            # Prune out images that are outright incompatible with the APK
            if min_sdk_version and max_sdk_version:
                for version, tag in image_to_sdk.items():
                    if int(version) >= int(min_sdk_version):
                        candidate_tags[version] = tag
                    if int(version) <= int(max_sdk_version):
                        candidate_tags[version] = tag

            # Choose the optimal based on the highest possible
            max_candidate = max(candidate_tags.keys())
            optimal_tag = candidate_tags[max_candidate]

        if not optimal_tag:
            self.logger.error("No optimal SDK version for this APK")
            return

        self.logger.info("Optimal tag resolved: {}".format(optimal_tag))

        # Start the docker container with the emulator

        container = client.containers.run(optimal_tag,
                                          # auto_remove=True,
                                          detach=True,
                                          environment={'ANDROID_ARCH':'x86'},
                                          privileged=True,
                                          volumes={'/dev/kvm':{'bind':'/dev/kvm', 'mode':'rw'}})

        connected = False
        max_attempts = 10
        # while attempts < max_attempts:
        #     # adb connect container.name:5555

        self.logger.info("Container started with ID: {}".format(container.id))
        #
        # container.stop()