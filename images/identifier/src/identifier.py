import base64
from datetime import datetime
import json
import hashlib
import os

import magic

from machina.core.worker import Worker
from machina.core.models.relationships.extracts import Extracts
from machina.core.models.relationships.retypedto import RetypedTo


class Identifier(Worker):
    """Identifier is the entrypoint to the system
    therefore, it does require any types, and can only be
    invoked directly by publishing to the Identifier queue
    """
    next_queues = []
    types = []

    def __init__(self, *args, **kwargs):
        super(Identifier, self).__init__(*args, **kwargs)
        
    def callback(self, data, properties):
        data = json.loads(data)
        binary_data = data['data']

        def _hash_data(data):
            result = {}
            for a in self.config['worker']['hash_algorithms']:
                h = hashlib.new(a, binary_data.encode()).hexdigest()
                result[a] = h
            return result

        def _resolve_supported_type(fpath):
            """attempt to resolve the type of a binary file
            against the high-level types loaded into the configuration
            Return a justification (e.g. the type, and the justification (e.g. mime, detailed)
            Prioritize detailed_types over mime
            """

            detailed_type = magic.from_file(fpath)
            for d, t in self.config['types']['detailed_types'].items():
                if detailed_type.lower().startswith(d.lower()):
                    return dict(type=t,
                                reason="detailed_types",
                                value=d)

            mime = magic.from_file(fpath, mime=True)
            for m, t in self.config['types']['mimes'].items():
                if mime == m:
                    return dict(type=t,
                                reason="mimes",
                                value=m)
            return None


        data_decoded = base64.b64decode(binary_data)

        # hash data_decoded
        hashes = _hash_data(data_decoded)

        # dir is time stamp
        ts = datetime.now()
        ts_fs = ts.strftime("%Y%m%d%H%M%S%f")
        ts_db = ts.strftime("%Y-%m-%d %H:%M:%S.%f")
        binary_dir = os.path.join(self.config['paths']['binaries'], ts_fs)
        if not os.path.isdir(binary_dir):
            os.makedirs(binary_dir)

        # fname is md5
        binary_fpath = os.path.join(binary_dir, hashes['md5'])
        with open(binary_fpath, 'wb') as f:
            f.write(data_decoded)

        # file size
        size = os.path.getsize(binary_fpath)

        # Flag to see if a manually-set type is supported
        supported_type = False

        # If type was specified, take that as ground truth
        if 'type' in data.keys():
            resolved_type = data['type']
            resolved = dict(type=resolved_type,
                            reason="provided",
                            value=None)
            if resolved_type in self.config['types']['available_types']:
                supported_type = True
        # Else, attempt to derive it using magic
        else:
            resolved = _resolve_supported_type(binary_fpath)
            if resolved:
                resolved_type = resolved['type']
                supported_type = True
            else:
                # If not resolved to a supported Machine type, tag it with a mime
                # and it will become an Artifact node
                mime = magic.from_file(binary_fpath, mime=True)
                self.logger.warn(f"{binary_fpath} type couldn't be resolved to supported type, is it supported? defaulted to mime type ({mime})")
                resolved_type = mime 

        self.logger.info(f"resolved to: {resolved}")

        body = {'ts': ts_fs,
                'hashes': hashes,
                'type': resolved_type}

        if supported_type:
            # Create DB entry with the supported Node type

            # Dynamic class resolution for Machina type -> OrientDB Node class
            # These are coupled tightly, a Node class' element_type attribute is named the same as a type
            # and the search ignores case
            c = self.resolve_db_node_cls(resolved_type)
            node = c.objects.create(md5=body['hashes']['md5'],
                                    sha256=body['hashes']['sha256'],
                                    size=size,
                                    ts=ts_db,
                                    type=resolved_type)
        else:
            # Create a generic entry (Artifact)
            node = self.graph.artifacts.create(md5=body['hashes']['md5'],
                sha256=body['hashes']['sha256'],
                size=size,
                ts=ts_db,
                type=resolved_type)

        body['id'] = node._id

        # If specified, link to another run's artifact
        # This is useful during the retyping process
        # Or to assert a link manually
        origin_node = None
        if 'origin' in data.keys():
            # Retrieve the originating Node cls from the database
            origin_node = self.graph.get_vertex(data['origin']['id'])

        # If the resolved originating hash matches the given hash
        # this is a retype of a previous Node.
        # If no match, it's an extraction
        if origin_node:
            if origin_node.md5 == body['hashes']['md5']:
                # create relationship (retype) btwn a and origin_a
                # https://stackoverflow.com/questions/51703088/pyorient-create-an-edge-in-orientdb-without-using-raw-query
                self.logger.info("Establishing retype link")
                self.create_edge(RetypedTo, origin_node._id, node._id)
                # e.g.  rat_eats_pea = g.eats.create(queried_rat, queried_pea, modifier='lots')

            else:
                # create relationship (extraction) btwn a and origin_a
                # graph.create_edge(Friend, orientRecord1, orientRecord2)
                self.logger.info("Establishing extraction link")
                self.create_edge(Extracts, origin_node._id, node._id)


        if resolved_type and supported_type:
            # publish to resolved type routing key
            channel = self.get_channel(self.config['rabbitmq'])
            channel.basic_publish(exchange='machina',
                routing_key=resolved_type,
                body=json.dumps(body))

            channel = self.get_channel(self.config['rabbitmq'])
            # publish to wildcard routing key
            channel.basic_publish(exchange='machina',
                routing_key='*',
                body=json.dumps(body))