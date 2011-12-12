#!/usr/bin/env python
"""Unititest for NotaryParser class"""

import os.path
import unittest

class TestNotaryParser(unittest.TestCase):
    """Tests for NotaryParser class"""

    notary_file = os.path.join(os.path.dirname(os.path.abspath( __file__ )),
                               "./http_notary_list.txt")

    def test_init(self):
        """Test basic creation of NotaryParser"""
        from Perspectives import NotaryParser
        parser = NotaryParser()

    def test_parse_file(self):
        """Test NotaryParser.parse_file()"""
        from Perspectives import NotaryParser
        parser = NotaryParser()
        notaries = parser.parse_file(self.notary_file)
        self.assertIsNotNone(notaries)
        self.assertEqual(len(notaries), 4)
        for notary in notaries:
            self.assertIsNotNone(notary.hostname)
            self.assertIsNotNone(notary.port)
            self.assertIsNotNone(notary.public_key)

if __name__ == "__main__":
    unittest.main()
