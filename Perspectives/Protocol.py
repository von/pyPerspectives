"""Perspectives Protocol implementation"""

import base64
import struct
import xml.dom.minidom

from Exceptions import NotaryResponseException
from Exceptions import NotaryResponseBadSignature
from Fingerprint import Fingerprint
from NotaryResponse import NotaryResponse
from NotaryResponse import NotaryResponseKey
from NotaryResponse import NotaryResponseTimeSpan
from Service import ServiceType

class Protocol:

    _str = "Perspectives"

    def __init__(self, notary, service):
        """Create a protocol instance

        notary - notary to query
        service - server to query about"""
        self.notary = notary
        self.service = service

    def __str__(self):
        return self._str

    @classmethod
    def get_name(cls):
        """Return protocol name"""
        return cls._str

    def get_url(self):
        """Return the URL to use to query for the given service"""
        url = "http://%s:%s/?host=%s&port=%s&service_type=%s" % (
            self.notary.hostname,
            self.notary.port,
            self.service.hostname,
            self.service.port,
            self.service.type)
        return url

    def parse_response(self, xml_data):
        """Parse response data, returning NotaryResponse instance"""
        dom = xml.dom.minidom.parseString(xml_data)
        doc_element = dom.documentElement
        if doc_element.tagName != "notary_reply":
            raise NotaryResponseException(
                "Unrecognized document element: %s" % doc_element.tagName)
        version = doc_element.getAttribute("version")
        sig_type = doc_element.getAttribute("sig_type")
        # Convert signature from base64 to raw form
        sig = base64.standard_b64decode(doc_element.getAttribute("sig"))
        keys = doc_element.getElementsByTagName("key")
        keys = [self._parse_key(key) for key in keys]
        response = NotaryResponse(self.notary,
                                  version,
                                  keys,
                                  sig_type,
                                  sig,
                                  xml_data)
        self.verify_response(response)
        return response

    def _parse_key(self, dom):
        """Create NotaryResponseKey from dom instance"""
        if dom.tagName != "key":
            raise NotaryResponseException("Unrecognized key element: %s" % (dom.tagName))
        type = ServiceType.from_string(dom.getAttribute("type"))
        key = Fingerprint.from_string(dom.getAttribute("fp"))
        timespans = [self._parse_timespan(e)
                     for e in dom.getElementsByTagName("timestamp")]
        return NotaryResponseKey(type, key, timespans)

    def _parse_timespan(self, dom):
        """Create NoraryResponseTimeSpan from dom"""
        if dom.tagName != "timestamp":
            raise NotaryResponseException("Unrecognized timespan element: %s" % (dom.tagName))
        start = int(dom.getAttribute("start"))
        end = int(dom.getAttribute("end"))
        return NotaryResponseTimeSpan(start, end)

    def verify_response(self, response):
        """Verify signature of response

        Raise NotaryResponseBadSignature on bad signature."""
        data = self._get_verify_data(response)

        notary_pub_key = self.notary.public_key
        notary_pub_key.reset_context(response.sig_type)
        notary_pub_key.verify_init()
        notary_pub_key.verify_update(data)
        result = notary_pub_key.verify_final(response.sig)
        if result == 0:
            raise NotaryResponseBadSignature("Signature verification failed")
        elif result != 1:
            raise NotaryResponseException("Error verifying signature")

    def _get_verify_data(self, response):
        """Return data for signature verification.

        Signature is over binary block composed of:
            Service id as a string ('hostname:port,type')
            One nul byte (Not sure what this is for)
            Response binary blob -- see NotaryResponse.bytes()
            """
        data = bytearray(b"%s:%s,%s" % (self.service.hostname,
                                        self.service.port,
                                        self.service.type))
        # One byte of zero  - unknown what this represents
        data.append(struct.pack("B", 0))
        data.extend(response.bytes())
        return data
