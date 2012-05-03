"""Parser for Notaries"""

import json
import M2Crypto
import unicodedata

from Perspectives import NotaryException
from Perspectives import Notary
from Perspectives import Notaries

from Protocol import Protocol

def unicode_to_string(u):
    """Convert a unicode string to a normal string"""
    return unicodedata.normalize('NFKD', u).encode('ascii','ignore')

class NotaryParser:
    """Parse serialized Notaries and return a Notaries instance"""
    
    def parse_file(self, path):
        """Return Notaries described in file.

        See parse_stream() for expected format"""
        with file(path, "r") as stream:
            notaries = self.parse_stream(stream)
        return notaries

    def parse_stream(self, stream):
        """Return Notaries described in stream.

        Expected format for the stream is a Convergence JSON bundle."""
        notaries = Notaries()
        d = json.load(stream)
        if d["version"] != 1:
            raise ValueError("Unrecognized Convergence bundle version: %d" % d["version"])
        for host_dict in d["hosts"]:
            notary = self._parse_notary(host_dict)
            notaries.append(notary)
        return notaries

    @classmethod
    def _parse_notary(cls, d):
        """Return Notary in given dictionary created from parsing a Bundle's JSON."""
        # JSON parser creates unicode by default
        cert_str = unicode_to_string("".join(d["certificate"]))
        cert = cls._certificate_from_string(cert_str)
        # Ignore http_port
        return Notary(unicode_to_string(d["host"]),
                      d["ssl_port"],
                      cert.get_pubkey(),
                      protocol_class=Protocol)

    @classmethod
    def _certificate_from_string(cls, s):
        """Read and return certificateas a M2Crypto.X509.X509 object from lines"""
        cert = M2Crypto.X509.load_cert_string(s)
        return cert
