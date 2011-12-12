#!/usr/bin/env python
"""Unittests for Notaries class"""

import os.path
import unittest

class TestNotaries(unittest.TestCase):
    """Tests for Notaries class"""
    
    notary_file = os.path.join(os.path.dirname(os.path.abspath( __file__ )),
                               "./http_notary_list.txt")

    def test_init(self):
        """Test basic creation of Notaries class"""
        from Perspectives import Notaries
        notaries = Notaries()
        self.assertIsNotNone(notaries)

    def test_default_notaries(self):
        """Test default_notaries()"""
        from Perspectives import default_notaries
        notaries = default_notaries()
        self.assertIsNotNone(notaries)
        self.assertEqual(len(notaries), 8)
        for notary in notaries:
            self.assertIsNotNone(notary.hostname)
            self.assertIsNotNone(notary.port)
            self.assertIsNotNone(notary.public_key)

    def test_find_notary(self):
        """Test find_notary()"""
        from Perspectives import NotaryParser
        notaries = NotaryParser().parse_file(self.notary_file)
        for hostname in [
            "cmu.ron.lcs.mit.edu",
            "convoke.ron.lcs.mit.edu",
            "mvn.ron.lcs.mit.edu",
            "hostway.ron.lcs.mit.edu"
            ]:
            notary = notaries.find_notary(hostname)
            self.assertIsNotNone(notary)
            self.assertEqual(notary.hostname, hostname)
        notary = notaries.find_notary("cmu.ron.lcs.mit.edu", port=8080)
        self.assertIsNotNone(notary)
        self.assertEqual(notary.hostname, "cmu.ron.lcs.mit.edu")
        # Test a failure
        notary = notaries.find_notary("does.not.exist")
        self.assertIsNone(notary)

if __name__ == "__main__":
    unittest.main()
