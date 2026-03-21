import base64
import hashlib
import json
import logging
import pathlib
import time
import unittest
from zipfile import ZipFile

from machina.core.models import GIF, HTML, JPEG, PNG, Zip
from tests.common import db_set_config, get_rmq_conn, test_data_dir

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TestUnzip(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db_set_config()
        cls.conn = get_rmq_conn()
        cls.channel = cls.conn.channel()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_unzip(self):
        """test that a zip file is correctly identified and its contents are
        extracted and identified with the correct node types"""
        MAX_RETRIES = 10

        zip_file = pathlib.Path(
            test_data_dir,
            'test_identifier',
            'test_unzip',
            'test2.zip').resolve()

        with open(zip_file, 'rb') as f:
            zip_data = f.read()
            zip_md5 = hashlib.md5(zip_data).hexdigest()
            zip_encoded = base64.b64encode(zip_data).decode()

        # Compute md5 of each file in the zip for node lookup
        content_md5s = {}
        with ZipFile(zip_file) as zf:
            for name in zf.namelist():
                if not name.endswith('/'):
                    content_md5s[pathlib.Path(name).name] = hashlib.md5(zf.read(name)).hexdigest()

        self.channel.basic_publish(
            exchange='',
            routing_key='Identifier',
            body=json.dumps({'data': zip_encoded})
        )

        zip_node = None
        png_node = None
        gif_node = None
        jpeg_node = None
        html_node = None

        # Wait for Zip node
        for _ in range(MAX_RETRIES):
            zip_node = Zip.nodes.get_or_none(md5=zip_md5)
            if not zip_node:
                time.sleep(2)
                logger.info(f"Checking for Zip Node with md5={zip_md5} in db...")
                continue
            else:
                logger.info(f"Found Zip md5={zip_md5}")
                break

        # Wait for PNG node (photoshop-8x12-16colorpalette.png)
        png_md5 = content_md5s['photoshop-8x12-16colorpalette.png']
        for _ in range(MAX_RETRIES):
            png_node = PNG.nodes.get_or_none(md5=png_md5)
            if not png_node:
                time.sleep(2)
                logger.info(f"Checking for PNG Node with md5={png_md5} in db...")
                continue
            else:
                logger.info(f"Found PNG md5={png_md5}")
                break

        # Wait for GIF node (mspaint-10x10.gif)
        gif_md5 = content_md5s['mspaint-10x10.gif']
        for _ in range(MAX_RETRIES):
            gif_node = GIF.nodes.get_or_none(md5=gif_md5)
            if not gif_node:
                time.sleep(2)
                logger.info(f"Checking for GIF Node with md5={gif_md5} in db...")
                continue
            else:
                logger.info(f"Found GIF md5={gif_md5}")
                break

        # Wait for JPEG node (Canon_40D_photoshop_import.jpg)
        jpg_md5 = content_md5s['Canon_40D_photoshop_import.jpg']
        for _ in range(MAX_RETRIES):
            jpeg_node = JPEG.nodes.get_or_none(md5=jpg_md5)
            if not jpeg_node:
                time.sleep(2)
                logger.info(f"Checking for JPEG Node with md5={jpg_md5} in db...")
                continue
            else:
                logger.info(f"Found JPEG md5={jpg_md5}")
                break

        # Wait for HTML node (test.html)
        html_md5 = content_md5s['test.html']
        for _ in range(MAX_RETRIES):
            html_node = HTML.nodes.get_or_none(md5=html_md5)
            if not html_node:
                time.sleep(2)
                logger.info(f"Checking for HTML Node with md5={html_md5} in db...")
                continue
            else:
                logger.info(f"Found HTML md5={html_md5}")
                break

        try:
            self.assertIsNotNone(zip_node)
            self.assertIsNotNone(png_node)
            self.assertIsNotNone(gif_node)
            self.assertIsNotNone(jpeg_node)
            self.assertIsNotNone(html_node)
        finally:
            for node in [zip_node, png_node, gif_node, jpeg_node, html_node]:
                if node:
                    node.delete()
