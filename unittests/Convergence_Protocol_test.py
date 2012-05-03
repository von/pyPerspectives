#!/usr/bin/env python
"""Unittests for Protocol class"""

import unittest

from ConvergenceTestCase import ConvergenceTestCase

class TestProtocol(ConvergenceTestCase):
    """Tests for Convergence.Protocol class"""

    def _create_procotol(self):
        from Convergence import Protocol
        notaries = self.get_test_notaries()
        service = self.get_test_service()
        # Choose notary that signed our test responses
        notary = notaries.find_notary("notary.thoughtcrime.org")
        return Protocol(notary, service)
        
    def test_init(self):
        """Test basic Protocol creation"""
        from Convergence import Protocol
        notaries = self.get_test_notaries()
        service = self.get_test_service()
        protocol = Protocol(notaries[0], service)
        self.assertIsNotNone(protocol)
        self.assertEqual(str(protocol), "Convergence")
        self.assertIsNotNone(protocol.get_url())

    def test_response_verify(self):
        """Test verification of response"""
        from Convergence import NotaryResponse
        from Convergence import Protocol
        from Convergence import Service, ServiceType
        notaries = self.get_test_notaries()
        notary = notaries.find_notary("notary.thoughtcrime.org")
        service = Service("example.google.com",
                          443,
                          ServiceType.SSL)
        protocol = Protocol(notary, service)
        response_string = self.load_response(
            "Convergence-response-notary.thoughtcrime.org")
        response = protocol.parse_response(response_string)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, NotaryResponse)

    def test_response_verify_failure(self):
        """Test failed verification of response"""
        from Convergence import NotaryResponse
        from Convergence import NotaryResponseBadSignature
        from Convergence import Protocol
        from Convergence import Service, ServiceType
        notaries = self.get_test_notaries()
        notary = notaries.find_notary("notary.thoughtcrime.org")
        service = Service("example.google.com",
                          443,
                          ServiceType.SSL)
        protocol = Protocol(notary, service)
        response_string = self.load_response(
            "Convergence-bad-response-notary.thoughtcrime.org")
        with self.assertRaises(NotaryResponseBadSignature):
            response = protocol.parse_response(response_string)
        
if __name__ == "__main__":
    unittest.main()


    
