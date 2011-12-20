#!/usr/bin/env python
"""Unittests for Protocol class"""

import unittest

import testutils

class TestProtocol(unittest.TestCase):
    """Tests for Protocol class"""

    def _create_procotol(self):
        from Perspectives import Protocol
        notaries = testutils.test_notaries()
        service = testutils.test_service()
        # Choose notary that signed our test responses
        notary = notaries.find_notary("cmu.ron.lcs.mit.edu")
        return Protocol(notary, service)
        
    def test_init(self):
        """Test basic Protocol creation"""
        from Perspectives import Protocol
        notaries = testutils.test_notaries()
        service = testutils.test_service()
        protocol = Protocol(notaries[0], service)
        self.assertIsNotNone(protocol)

    def test_response_verify(self):
        """Test verification of response"""
        from Perspectives import NotaryResponse
        from Perspectives import Protocol
        from Perspectives import Service, ServiceType
        notaries = testutils.test_notaries()
        notary = notaries.find_notary("cmu.ron.lcs.mit.edu")
        service = Service("www.citibank.com",
                                       443,
                                       ServiceType.SSL)
        protocol = Protocol(notary, service)
        response_string = testutils.load_response("response.1")
        response = protocol.parse_response(response_string)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, NotaryResponse)

    def test_response_verify_failure(self):
        """Test failed verification of response"""
        from Perspectives import NotaryResponse
        from Perspectives import NotaryResponseBadSignature
        from Perspectives import Protocol
        from Perspectives import Service, ServiceType
        notaries = testutils.test_notaries()
        notary = notaries.find_notary("cmu.ron.lcs.mit.edu")
        service = Service("www.citibank.com",
                                       443,
                                       ServiceType.SSL)
        protocol = Protocol(notary, service)
        response_string = testutils.load_response("response-bad.1")
        with self.assertRaises(NotaryResponseBadSignature):
            protocol.parse_response(response_string)
        
if __name__ == "__main__":
    unittest.main()


    
