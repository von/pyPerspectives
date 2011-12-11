"""Class for representing a certificate fingerprint"""

import binascii
import M2Crypto

from Exceptions import FingerprintException

class Fingerprint:
    """Fingerprint from certificate"""
    
    def __init__(self, data):
        """Create a Fingerprint instance with given binary data"""
        self.data = bytes(data)

    @classmethod
    def from_string(cls, str):
        """Create Fingerprint from hex colon-separated word format"""
        data = bytearray([int(n,16) for n in str.split(":")])
        return cls(data)

    @classmethod
    def from_M2Crypto_X509(cls, cert):
        """Create Fingerprint from M2Crypto.X509.X509 instance."""
        # Data will be hex string without colons
        # M2Crypto drops leading zeros, so we pad out with zeros to 32
        # characters (==128 bits of MD5)
        fingerprint = cert.get_fingerprint().rjust(32, "0")
        try:
            data = binascii.a2b_hex(fingerprint)
        except Exception as e:
            raise FingerprintException("Error parsing fingerprint \"%s\": %s" % (fingerprint, str(e)))
        return cls(data)

    @classmethod
    def from_certificate_PEM(cls, pem):
        """Create Fingerprint from certificate in PEM format."""
        cert = M2Crypto.X509.load_cert_string(pem)
        return cls.from_M2Crypto_X509(cert)

    def __str__(self, sep=":"):
        return sep.join([binascii.b2a_hex(b) for b in self.data])

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return self.data != other.data
