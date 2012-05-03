"""Convergence Protocol implementation"""

import base64
import json
import struct

import Perspectives
from Perspectives import Fingerprint
from Perspectives import NotaryResponse
from Perspectives import NotaryResponseKey
from Perspectives import NotaryResponseTimeSpan

class Protocol(Perspectives.Protocol):
    """Convergence Protocol"""

    _str = "Convergence"

    def get_url(self):
        """Return the URL to use to query for the given service"""
        url = "https://%s:%d/target/%s+%d" % (
            self.notary.hostname,
            self.notary.port,
            self.service.hostname,
            self.service.port)
        return url

    def parse_response(self, data):
        """Parse response data, returning NotaryResponse instance"""
        d = json.loads(data)
        key_list = d["fingerprintList"]
        keys = [self._parse_key(key) for key in key_list]
        sig = base64.standard_b64decode(d["signature"])
        # Signature type and version are implicit with Convergence
        version="1"
        sig_type = "sha1"
        response = NotaryResponse(self.notary,
                                  version,
                                  keys,
                                  sig_type,
                                  sig,
                                  data)
        self.verify_response(response)
        return response

    def _parse_key(self, d):
        """Create NotaryResponseKey from dom instance"""
        type = "XXX"  # XXX Not sure what this should be
        key = Fingerprint.from_string(d["fingerprint"])
        timespans = [self._parse_timespan(d["timestamp"])]
        return NotaryResponseKey(type, key, timespans)

    def _parse_timespan(self, d):
        """Create NoraryResponseTimeSpan from dictionary"""
        start = int(d["start"])
        end = int(d["finish"])
        return NotaryResponseTimeSpan(start, end)

    def _get_verify_data(self, response):
        """Return data for signature verification.

        Quoting https://github.com/moxie0/Convergence/wiki/Notary-Protocol:
        The signature is valid for the same JSON data, with the signature and
        all excess spaces and newlines removed. Basically the signed data is
        exactly "{fingerprintList:[...]}" where ... is replaced by the actual
        fingerprints.

        Basically we strip the signature from the JSON and return it.
        """
        d = json.loads(response.raw_response)
        del d["signature"]
        data = json.dumps(d)
        return data
