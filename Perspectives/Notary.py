"""Class for representing Perspective Notaries"""

import logging
import struct
import urllib

from Exceptions import NotaryException
from Exceptions import NotaryResponseBadSignature
from Exceptions import NotaryResponseException
from Exceptions import NotaryUnknownServiceException
from Notary_dispatcher import Notary_dispatcher
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

    def get_dispatcher(self, service, dispatcher_map=None):
        """Return Notary_dispatcher to query Notary for given service"""
        url = self.get_url(service)
        return Notary_dispatcher(url, dispatcher_map)

    def get_url(self, service):
        """Return the URL to use to query for the given service"""
        url = "http://%s:%s/?host=%s&port=%s&service_type=%s" % (self.hostname, self.port, service.hostname, service.port, service.type)
        return url

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

