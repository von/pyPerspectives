#!/usr/bin/env python
"""Unittests for NotaryResponse class"""

import os.path
import unittest

import testutils

class TestNotaryResponse(unittest.TestCase):
    """Tests for NotaryResponse class"""

    def test_basic(self):
        """Test basic NotaryResponse and NotaryResponses creation"""
        response = testutils.create_NotaryResponse()
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.bytes())
        self.assertIsNotNone(response.last_key_seen())
        self.assertIsNotNone(response.key_change_times())

    def test_last_key_seen(self):
        """Test last_key_seen()"""
        from Perspectives import ServiceKey
        from Perspectives import ServiceType
        response = testutils.create_NotaryResponse()
        key = response.last_key_seen()
        expected_key = ServiceKey.from_string(
            ServiceType.SSL,
            "87:71:5c:d4:7b:66:fd:9f:96:79:ba:0f:3e:15:b7:e3")
        self.assertEqual(key, expected_key,
                         "%s != %s" % (key, expected_key))

if __name__ == "__main__":
    unittest.main()
