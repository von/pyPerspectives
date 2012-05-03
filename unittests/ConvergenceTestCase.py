"""TestCase base class for Convergence tests"""

import os.path
import unittest

import M2Crypto

class ConvergenceTestCase(unittest.TestCase):
    """TestCase base class for Convergence tests"""

    my_path = os.path.dirname(os.path.abspath( __file__ ))

    notary_file = os.path.join(os.path.dirname(os.path.abspath( __file__ )),
                               "./thoughtcrime.notary")

    @classmethod
    def get_test_notaries(cls):
        """Return a Notaries instance with our test notaries"""
        from Convergence import NotaryParser
        parser = NotaryParser()
        notaries = parser.parse_file(cls.notary_file)
        return notaries

    @staticmethod
    def get_test_service():
        """Return test Service"""
        from Convergence import Service
        return Service("test.example.com", 443)

    @classmethod
    def load_response(cls, filename):
        """Load the response given by the filename"""
        with open(os.path.join(cls.my_path, filename)) as f:
            response_string = "".join(f.readlines())
        return response_string

    def validate_Notary(self, notary):
        """Run a Notary instance through a battery of tests."""
        from Convergence import Protocol
        self.assertIsNotNone(notary)
        self.assertIsNotNone(notary.hostname)
        self.assertIsNotNone(notary.port)
        self.assertIsNotNone(notary.public_key)
        self.assertIsInstance(notary.public_key, M2Crypto.EVP.PKey)

        # Test get_protocol()
        self.assertEqual(notary.protocol_class, Protocol)
        service = self.get_test_service()
        protocol = notary.get_protocol(service)
        self.assertIsNotNone(protocol)
        self.assertIsInstance(protocol, Protocol)
