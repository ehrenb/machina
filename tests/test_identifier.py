import base64
import hashlib
import json
import logging
import pathlib
import time
import unittest

from machina.core.models import JPEG
from tests.common import db_set_config, get_rmq_conn, test_data_dir

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
class TestIdentifier(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        db_set_config()
        cls.conn = get_rmq_conn()
        cls.channel = cls.conn.channel()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_provided_type(self):
        """test that type is set when provided manually by user"""
        MAX_RETRIES = 5

        png_file = pathlib.Path(test_data_dir, 'test_identifier', 'google.png').resolve()

        with open(png_file, 'rb') as f:
            logger.info(f'Submitting {png_file}')
            png_data = f.read()
            png_md5 = hashlib.md5(png_data).hexdigest()
            data_encoded = base64.b64encode(png_data).decode()

            data = json.dumps({
                'data': data_encoded,
                'type': 'jpeg'          # assert JPEG instead of PNG
            })

            self.channel.basic_publish(
                exchange='',
                routing_key='Identifier',
                body=data
            )

            # wait for JPEG node to be created, and validate it
            for _ in range(MAX_RETRIES):
                new_jpeg_node = JPEG.nodes.get_or_none(md5=png_md5)
                if not new_jpeg_node:
                    time.sleep(2)
                    logger.info(f"Checking for JPEG Node with md5={png_md5} in db...")
                    continue
                else:
                    logger.info(f"Found md5={png_md5}")
                    break

            self.assertIsNotNone(new_jpeg_node)

            # TODO use venv to test this out

    def test_resolve_via_detailed_type(self):
        """test that type is set using detailed type magic"""
        pass

    def test_resolve_via_mime_type(self):
        """test that type is et using mime type magic"""
        pass

    def test_unresolved_type(self):
        """test unresolved type should have a 'type' = 'artifact'"""
        pass