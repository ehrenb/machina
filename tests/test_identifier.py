import base64
import hashlib
import json
import logging
import pathlib
import time
import unittest

from neomodel import db

from machina.core.models import Artifact, HTML, JFFS2, JPEG
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

        new_jpeg_node = None
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

        try:
            self.assertIsNotNone(new_jpeg_node)
        finally:
            if new_jpeg_node:
                new_jpeg_node.delete()

    def test_resolve_via_detailed_type(self):
        """test that type is set using detailed type magic"""
        MAX_RETRIES = 5

        jffs2_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_resolve_via_detailed_type',
            'firmware.jffs2').resolve()

        new_jffs2_node = None
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

        try:
            self.assertIsNotNone(new_jffs2_node)
        finally:
            if new_jffs2_node:
                new_jffs2_node.delete()

    def test_resolve_via_mime_type(self):
        """test that type is set using mime type magic"""
        MAX_RETRIES = 5

        html_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_resolve_via_mime_type',
            'test.html').resolve()

        new_html_node = None
        with open(html_file, 'rb') as f:
            logger.info(f'Submitting {html_file}')
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

            for _ in range(MAX_RETRIES):
                new_html_node = HTML.nodes.get_or_none(md5=md5)
                if not new_html_node:
                    time.sleep(2)
                    logger.info(f"Checking for HTML Node with md5={md5} in db...")
                    continue
                else:
                    logger.info(f"Found md5={md5}")
                    break

        try:
            self.assertIsNotNone(new_html_node)
        finally:
            if new_html_node:
                new_html_node.delete()

    def test_origin_extraction(self):
        """test that an extraction relationship is created when origin is provided with a different md5"""
        MAX_RETRIES = 5

        # Submit the origin file first
        origin_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_unresolved_type',
            'artifact.txt').resolve()

        with open(origin_file, 'rb') as f:
            logger.info(f'Submitting origin {origin_file}')
            origin_data = f.read()
            origin_md5 = hashlib.md5(origin_data).hexdigest()
            origin_encoded = base64.b64encode(origin_data).decode()

            self.channel.basic_publish(
                exchange='',
                routing_key='Identifier',
                body=json.dumps({'data': origin_encoded})
            )

        origin_node = None
        for _ in range(MAX_RETRIES):
            origin_node = Artifact.nodes.get_or_none(md5=origin_md5)
            if not origin_node:
                time.sleep(2)
                logger.info(f"Checking for origin Artifact Node with md5={origin_md5} in db...")
                continue
            else:
                logger.info(f"Found origin md5={origin_md5}")
                break

        self.assertIsNotNone(origin_node)

        # Submit a different file with origin pointing to the first node
        extracted_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_resolve_via_mime_type',
            'test.html').resolve()

        with open(extracted_file, 'rb') as f:
            logger.info(f'Submitting extracted {extracted_file}')
            extracted_data = f.read()
            extracted_md5 = hashlib.md5(extracted_data).hexdigest()
            extracted_encoded = base64.b64encode(extracted_data).decode()

            self.channel.basic_publish(
                exchange='',
                routing_key='Identifier',
                body=json.dumps({
                    'data': extracted_encoded,
                    'origin': {
                        'uid': origin_node.uid,
                        'type': 'artifact',
                        'md5': origin_node.md5,
                        'ts': origin_node.ts.strftime("%Y%m%d%H%M%S%f")
                    }
                })
            )

        extracted_node = None
        for _ in range(MAX_RETRIES):
            extracted_node = HTML.nodes.get_or_none(md5=extracted_md5)
            if not extracted_node:
                time.sleep(2)
                logger.info(f"Checking for extracted HTML Node with md5={extracted_md5} in db...")
                continue
            else:
                logger.info(f"Found extracted md5={extracted_md5}")
                break
        
        time.sleep(1)

        try:
            self.assertIsNotNone(extracted_node)
            # is_connected() cannot be used here because the extracts relationship
            # targets the abstract Base class, which has no __label__ attribute.
            # neomodel's traversal query builder requires a concrete class label,
            # so a raw Cypher query is used instead.
            results, _ = db.cypher_query(
                "MATCH (a)-[:EXTRACTS]->(b) WHERE a.uid = $origin_uid AND b.uid = $extracted_uid RETURN count(b) > 0",
                {'origin_uid': origin_node.uid, 'extracted_uid': extracted_node.uid})
            self.assertTrue(results[0][0])
        finally:
            if extracted_node:
                extracted_node.delete()
            if origin_node:
                origin_node.delete()

    def test_origin_retype(self):
        """test that a retype relationship is created when origin is provided with the same md5"""
        MAX_RETRIES = 5

        jffs2_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_resolve_via_detailed_type',
            'firmware.jffs2').resolve()

        with open(jffs2_file, 'rb') as f:
            data = f.read()
            md5 = hashlib.md5(data).hexdigest()
            data_encoded = base64.b64encode(data).decode()

        # Submit the file as jffs2 to create the origin node
        logger.info(f'Submitting origin {jffs2_file}')
        self.channel.basic_publish(
            exchange='',
            routing_key='Identifier',
            body=json.dumps({'data': data_encoded, 'type': 'jffs2'})
        )

        origin_node = None
        for _ in range(MAX_RETRIES):
            origin_node = JFFS2.nodes.get_or_none(md5=md5)
            if not origin_node:
                time.sleep(2)
                logger.info(f"Checking for origin JFFS2 Node with md5={md5} in db...")
                continue
            else:
                logger.info(f"Found origin md5={md5}")
                break

        self.assertIsNotNone(origin_node)

        # Submit the same file with a different type and origin pointing to the first node.
        # Matching md5 triggers the retype branch.
        logger.info(f'Submitting retype {jffs2_file}')
        self.channel.basic_publish(
            exchange='',
            routing_key='Identifier',
            body=json.dumps({
                'data': data_encoded,
                'type': 'artifact',
                'origin': {
                    'uid': origin_node.uid,
                    'type': 'jffs2',
                    'md5': origin_node.md5,
                    'ts': origin_node.ts.strftime("%Y%m%d%H%M%S%f")
                }
            })
        )

        retyped_node = None
        for _ in range(MAX_RETRIES):
            retyped_node = Artifact.nodes.get_or_none(md5=md5)
            if not retyped_node:
                time.sleep(2)
                logger.info(f"Checking for retyped Artifact Node with md5={md5} in db...")
                continue
            else:
                logger.info(f"Found retyped md5={md5}")
                break

        time.sleep(1)

        try:
            self.assertIsNotNone(retyped_node)
            # is_connected() cannot be used here because the retyped relationship
            # targets the abstract Base class, which has no __label__ attribute.
            # neomodel's traversal query builder requires a concrete class label,
            # so a raw Cypher query is used instead.
            results, _ = db.cypher_query(
                "MATCH (a)-[:RETYPED]->(b) WHERE a.uid = $origin_uid AND b.uid = $retyped_uid RETURN count(b) > 0",
                {'origin_uid': origin_node.uid, 'retyped_uid': retyped_node.uid})
            self.assertTrue(results[0][0])
        finally:
            if retyped_node:
                retyped_node.delete()
            if origin_node:
                origin_node.delete()

    def test_unresolved_type(self):
        """test unresolved type, should be set to node type
        Artifact"""
        
        MAX_RETRIES = 5

        txt_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_unresolved_type',
            'artifact.txt').resolve()

        new_artifact_node = None
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

        try:
            self.assertIsNotNone(new_artifact_node)
        finally:
            if new_artifact_node:
                new_artifact_node.delete()
