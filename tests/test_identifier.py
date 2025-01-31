import base64
import hashlib
import json
import logging
import pathlib
import time
import unittest

from machina.core.models import Artifact, JFFS2, JPEG
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

        png_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_provided_type',
            'google.png').resolve()

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

    def test_resolve_via_detailed_type(self):
        """test that type is set using detailed type magic"""
        MAX_RETRIES = 5

        jffs2_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_resolve_via_detailed_type',
            'firmware.jffs2').resolve()

        with open(jffs2_file, 'rb') as f:
            logger.info(f'Submitting {jffs2_file}')
            data = f.read()
            md5 = hashlib.md5(data).hexdigest()
            data_encoded = base64.b64encode(data).decode()

            data = json.dumps({
                'data': data_encoded
            })

            self.channel.basic_publish(
                exchange='',
                routing_key='Identifier',
                body=data
            )

            # wait for generic Artifact
            # node to be created, and validate it
            for _ in range(MAX_RETRIES):
                new_jffs2_node = JFFS2.nodes.get_or_none(md5=md5)
                if not new_jffs2_node:
                    time.sleep(2)
                    logger.info(f"Checking for JFFS2 Node with md5={md5} in db...")
                    continue
                else:
                    logger.info(f"Found md5={md5}")
                    break

            self.assertIsNotNone(new_jffs2_node)

    # def test_resolve_via_mime_type(self):
    #     """test that type is et using mime type magic"""
    #     pass

    def test_unresolved_type(self):
        """test unresolved type, should be set to node type
        Artifact"""
        
        MAX_RETRIES = 5

        txt_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_unresolved_type',
            'artifact.txt').resolve()

        with open(txt_file, 'rb') as f:
            logger.info(f'Submitting {txt_file}')
            txt_data = f.read()
            txt_md5 = hashlib.md5(txt_data).hexdigest()
            data_encoded = base64.b64encode(txt_data).decode()

            data = json.dumps({
                'data': data_encoded
            })

            self.channel.basic_publish(
                exchange='',
                routing_key='Identifier',
                body=data
            )

            # wait for generic Artifact
            # node to be created, and validate it
            for _ in range(MAX_RETRIES):
                new_artifact_node = Artifact.nodes.get_or_none(md5=txt_md5)
                if not new_artifact_node:
                    time.sleep(2)
                    logger.info(f"Checking for Artifact Node with md5={txt_md5} in db...")
                    continue
                else:
                    logger.info(f"Found md5={txt_md5}")
                    break

            self.assertIsNotNone(new_artifact_node)
