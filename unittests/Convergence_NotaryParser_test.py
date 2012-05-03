#!/usr/bin/env python
"""Unititest for NotaryParser class"""

import os.path
import unittest

from ConvergenceTestCase import ConvergenceTestCase

class TestNotaryParser(ConvergenceTestCase):
    """Tests for NotaryParser class"""

    notary_file = os.path.join(os.path.dirname(os.path.abspath( __file__ )),
                               "./thoughtcrime.notary")

    def test_init(self):
        """Test basic creation of Convergence.NotaryParser"""
        from Convergence import NotaryParser
        parser = NotaryParser()

    def test_parse_file(self):
        """Test Convergence.NotaryParser.parse_file()"""
        from Convergence import NotaryParser
        parser = NotaryParser()
        notaries = parser.parse_file(self.notary_file)
        self.assertIsNotNone(notaries)
        self.assertEqual(len(notaries), 2)
        for notary in notaries:
            self.validate_Notary(notary)

if __name__ == "__main__":
    unittest.main()
