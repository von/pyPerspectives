"""Class for representing Perspective Notaries"""

import logging
import M2Crypto
import re
import struct
import urllib

from Exceptions import NotaryException
from Exceptions import NotaryResponseBadSignature
from Exceptions import NotaryResponseException
from Exceptions import NotaryUnknownServiceException
from NotaryResponse import NotaryResponse

class Notary:
    """Class for representing Perspective Notary"""

    def __init__(self, hostname, port, public_key):
        self.hostname = hostname
        self.port = port
        self.public_key = public_key
        self.logger = logging.getLogger("Perspectives.Notary")

    def __str__(self):
        return "Notary at %s port %s" % (self.hostname, self.port)

    def query(self, service):
        """Query notary regarding given service, returning NotaryResponse

        type may be with numeric value or 'https'"""
        url = self.get_url(service)
        try:
            stream = urllib.urlopen(url)
        except IOError as e:
            raise NotaryException("Error connecting to Notary %s: %s" % (self, str(e)))
        if stream.getcode() == 404:
            raise NotaryUnknownServiceException()
        elif stream.getcode() != 200:
            raise NotaryException("Got bad http response code (%s) from %s for %s" % (stream.getcode(), self, service))
        response = "".join(stream.readlines())
        stream.close()
        return NotaryResponse(response)

    def get_url(self, service):
        """Return the URL to use to query for the given service"""
        url = "http://%s:%s/?host=%s&port=%s&service_type=%s" % (self.hostname, self.port, service.hostname, service.port, service.type)
        return url

    @classmethod
    def from_stream(cls, stream):
        """Return Notary described in given stream.

        Expected format is:
        # Lines starting with '#' are comments and ignored
        <hostname>:<port>
        -----BEGIN PUBLIC KEY-----
        <multiple lines of Base64-encoded data>
        -----END PUBLIC KEY----

        If EOF is found before a Notary, returns None.
        """
        hostname, port, public_key = None, None, None
        hostname_port_re = re.compile("(\S+):(\d+)")
        for line in stream:
            line = line.strip()
            if line.startswith("#") or (line == ""):
                continue  # Ignore comments and blank lines
            match = hostname_port_re.match(line)
            if match is not None:
                hostname = match.group(1)
                port = int(match.group(2))
            elif line == "-----BEGIN PUBLIC KEY-----":
                if hostname is None:
                    raise NotaryException("Public key found without Notary")
                lines = [line + "\n"]
                for line in stream:
                    lines.append(line)
                    if line.startswith("-----END PUBLIC KEY-----"):
                        break
                else:
                    raise NotaryException("No closing 'END PUBLIC KEY' line for key found")
                public_key = cls._public_key_from_lines(lines)
                break  # End of Notary
            else:
                raise NotaryException("Unrecognized line: " + line)
        if hostname is None:
            # We hit EOF before finding a Notary
            return None
        if public_key is None:
            raise NotaryException("No public key found for Notary %s:%s" % (hostname, port))
        return cls(hostname, port, public_key)

    @classmethod
    def _public_key_from_lines(cls, lines):
        """Read and return public key from lines"""
        bio = M2Crypto.BIO.MemoryBuffer("".join(lines))
        pub_key = M2Crypto.EVP.PKey()
        pub_key.assign_rsa(M2Crypto.RSA.load_pub_key_bio(bio))
        return pub_key

    def verify_response(self, response, service):
        """Verify signature of response regarding given service.

        Raise NotaryResponseBadSignature on bad signature.

        Signature is over binary block composed of:
            Service id as a string ('hostname:port,type')
            One nul byte (Not sure what this is for)
            Response binary blob -- see NotaryResponse.bytes()
            """
        data = bytearray(b"%s:%s,%s" % (service.hostname,
                                            service.port,
                                            service.type))
        # One byte of zero  - unknown what this represents
        data.append(struct.pack("B", 0))

        data.extend(response.bytes())
        
        notary_pub_key = self.public_key
        # Todo: Assuming MD5 here, should double check response.type
        notary_pub_key.reset_context(md="md5")
        notary_pub_key.verify_init()
        notary_pub_key.verify_update(data)
        result = notary_pub_key.verify_final(response.sig)
        if result == 0:
            raise NotaryResponseBadSignature("Signature verification failed")
        elif result != 1:
            raise NotaryResponseException("Error verifying signature")

