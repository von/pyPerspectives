"""Classes for representing application services"""

import re
import ssl

from Fingerprint import Fingerprint

class Service:
    """Representation of a application service"""

    def __init__(self, hostname, port, type=None):
        """Create a Service instance.

        If type is non, guess based on port (not actually implemented)."""
        self.hostname = hostname
        self.port = port
        self.type = type if type is not None else ServiceType.SSL

    def __str__(self):
        return "%s:%s,%s" % (self.hostname, self.port, self.type)

    # ssl.get_server_certificate() doesn't terminate the PEM correctly,
    # it is missing a newline before the END line. This re detects that.
    bad_cert_end_re = re.compile("(\S)(-----END CERTIFICATE-----)$",
                                 re.MULTILINE)

    def get_fingerprint(self):
        """Return the Service's certificate fingerprint"""
        cert_pem = ssl.get_server_certificate((self.hostname, self.port))
        # Fix missing newline before END line
        cert_pem = self.bad_cert_end_re.sub(r"\1\n\2", cert_pem)
        return Fingerprint.from_certificate_PEM(cert_pem)

class ServiceType:
    """Constants for service types"""
    # Determined experimentally. I don't know where these are documented.
    HTTPS = 2
    SSL = 2

    STRINGS = {
        "ssl" : SSL
        }
    
    @classmethod
    def from_string(cls, str):
        """Return integer value from string"""
        return cls.STRINGS[str]
