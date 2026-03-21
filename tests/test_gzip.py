import base64
import gzip
import hashlib
import json
import logging
import pathlib
import time
import unittest

from machina.core.models import Gzip, PNG
from tests.common import db_set_config, get_rmq_conn, test_data_dir

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TestGzip(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db_set_config()
        cls.conn = get_rmq_conn()
        cls.channel = cls.conn.channel()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_gzip(self):
        """test that a gzip file is correctly identified and its decompressed
        content is submitted back to Identifier and assigned the correct node type"""
        MAX_RETRIES = 10

        gz_file = pathlib.Path(
            test_data_dir,
            'test_gzip',
            'test_gzip',
            'photoshop-8x12-16colorpalette.png.gz').resolve()

        with open(gz_file, 'rb') as f:
            gz_data = f.read()
            gz_md5 = hashlib.md5(gz_data).hexdigest()
            gz_encoded = base64.b64encode(gz_data).decode()

        # Compute md5 of the decompressed content for node lookup
        decompressed_md5 = hashlib.md5(gzip.decompress(gz_data)).hexdigest()

        self.channel.basic_publish(
            exchange='',
            routing_key='Identifier',
            body=json.dumps({'data': gz_encoded})
        )

        gz_node = None
        decompressed_node = None

        # Wait for Gzip node
        for _ in range(MAX_RETRIES):
            gz_node = Gzip.nodes.get_or_none(md5=gz_md5)
            if not gz_node:
                time.sleep(2)
                logger.info(f"Checking for Gzip Node with md5={gz_md5} in db...")
                continue
            else:
                logger.info(f"Found Gzip md5={gz_md5}")
                break

        # Wait for decompressed PNG node
        for _ in range(MAX_RETRIES):
            decompressed_node = PNG.nodes.get_or_none(md5=decompressed_md5)
            if not decompressed_node:
                time.sleep(2)
                logger.info(f"Checking for decompressed PNG Node with md5={decompressed_md5} in db...")
                continue
            else:
                logger.info(f"Found decompressed PNG md5={decompressed_md5}")
                break

        try:
            self.assertIsNotNone(gz_node)
            self.assertIsNotNone(decompressed_node)
        finally:
            for node in [gz_node, decompressed_node]:
                if node:
                    node.delete()
