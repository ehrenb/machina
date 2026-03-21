import base64
import bz2
import hashlib
import json
import logging
import pathlib
import time
import unittest

from machina.core.models import PNG, BZ2
from tests.common import db_set_config, get_rmq_conn, test_data_dir

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TestBz2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db_set_config()
        cls.conn = get_rmq_conn()
        cls.channel = cls.conn.channel()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_bz2(self):
        """test that a bz2 file is correctly identified and its decompressed
        content is submitted back to Identifier and assigned the correct node type"""
        MAX_RETRIES = 10

        bz2_file = pathlib.Path(
            test_data_dir,
            'test_bz2',
            'test_bz2',
            'photoshop-8x12-16colorpalette.png.bz2').resolve()

        with open(bz2_file, 'rb') as f:
            bz2_data = f.read()
            bz2_md5 = hashlib.md5(bz2_data).hexdigest()
            bz2_encoded = base64.b64encode(bz2_data).decode()

        # Compute md5 of the decompressed content for node lookup
        decompressed_md5 = hashlib.md5(bz2.decompress(bz2_data)).hexdigest()

        self.channel.basic_publish(
            exchange='',
            routing_key='Identifier',
            body=json.dumps({'data': bz2_encoded})
        )

        bz2_node = None
        decompressed_node = None

        # Wait for BZ2 node
        for _ in range(MAX_RETRIES):
            bz2_node = BZ2.nodes.get_or_none(md5=bz2_md5)
            if not bz2_node:
                time.sleep(2)
                logger.info(f"Checking for BZ2 Node with md5={bz2_md5} in db...")
                continue
            else:
                logger.info(f"Found BZ2 md5={bz2_md5}")
                break

        # Wait for decompressed Artifact node (plain text is not a supported type)
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
            self.assertIsNotNone(bz2_node)
            self.assertIsNotNone(decompressed_node)
        finally:
            for node in [bz2_node, decompressed_node]:
                if node:
                    node.delete()
