import json
import unittest

from tests.common import get_rmq_conn, test_data_dir

class TestIdentifier(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.conn = get_rmq_conn()
        cls.channel = cls.conn.channel()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_provided_type(self):
        """test that type is set when provided manually by user"""
        pass

    def test_resolve_via_detailed_type(self):
        """test that type is set using detailed type magic"""
        pass

    def test_resolve_via_mime_type(self):
        """test that type is et using mime type magic"""
        pass

    def test_unresolved_type(self):
        """test unresolved type should have a 'type' = 'artifact'"""
        pass