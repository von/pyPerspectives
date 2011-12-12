"""Parser for Notaries"""

import M2Crypto
import re

from Exceptions import NotaryException
from Notary import Notary
from Notaries import Notaries

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

        Expected format for each Notary is:
        # Lines starting with '#' are comments and ignored
        <hostname>:<port>
        -----BEGIN PUBLIC KEY-----
        <multiple lines of Base64-encoded data>
        -----END PUBLIC KEY----
        """
        notaries = Notaries()
        while True:
            notary = self._parse_notary(stream)
            if notary is None:  # EOF
                break
            else:
                notaries.append(notary)
        return notaries

    hostname_port_re = re.compile("(\S+):(\d+)")

    def _parse_notary(self, stream):
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
        for line in stream:
            line = line.strip()
            if line.startswith("#") or (line == ""):
                continue  # Ignore comments and blank lines
            match = self.hostname_port_re.match(line)
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
                    raise NotaryException(
                        "No closing 'END PUBLIC KEY' line for key found")
                public_key = self._public_key_from_lines(lines)
                break  # End of Notary
            else:
                raise NotaryException("Unrecognized line: " + line)
        if hostname is None:
            # We hit EOF before finding a Notary
            return None
        if public_key is None:
            raise NotaryException(
                "No public key found for Notary %s:%s" % (hostname, port))
        return Notary(hostname, port, public_key)

    @classmethod
    def _public_key_from_lines(cls, lines):
        """Read and return public key from lines"""
        bio = M2Crypto.BIO.MemoryBuffer("".join(lines))
        pub_key = M2Crypto.EVP.PKey()
        pub_key.assign_rsa(M2Crypto.RSA.load_pub_key_bio(bio))
        return pub_key
