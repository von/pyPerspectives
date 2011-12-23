"""Class for representing Perspective Notaries"""

import logging
import urllib

from Exceptions import NotaryException
from Exceptions import NotaryUnknownServiceException
from Notary_dispatcher import Notary_dispatcher
from Protocol import Protocol

class Notary:
    """Class for representing Perspective Notary"""

    def __init__(self, hostname, port, public_key, protocol_class=Protocol):
        self.hostname = hostname
        self.port = port
        self.public_key = public_key
        self.logger = logging.getLogger("Perspectives.Notary")
        self.protocol_class = protocol_class

    def __str__(self):
        return "%s notary at %s port %s" % (self.protocol_class.get_name(),
                                            self.hostname,
                                            self.port)

    def query(self, service):
        """Query notary regarding given service, returning NotaryResponse"""
        protocol = self.get_protocol(service)
        url = protocol.get_url(service)
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
        return protocol.parse_response(response)

    def defered_query(self, service):
        """Query Notary. Returns a Deferred instance.

        For CallBacks, the argument will be a NotaryResponse instance.
        For ErrBacks, the Failure will have a notary attribute being the Notary.

        For ErrBack, the Failure will have a notary attribute being the Notary."""
        from twisted.web.client import getPage
        protocol = self.get_protocol(service)
        url = protocol.get_url()
        d = getPage(url)
        # Convert raw response into NotaryResponse before return to our caller
        d.addCallback(protocol.parse_response)
        # For Errback, add Notary to Failure
        def _augment_failure(err):
            err.notary = self
            return err
        d.addErrback(_augment_failure)
        return d

    def get_dispatcher(self, service, dispatcher_map=None):
        """Return Notary_dispatcher to query Notary for given service"""
        return Notary_dispatcher(self, service, dispatcher_map)

    def get_protocol(self, service):
        """Return Protocol instance to query regarding service"""
        return self.protocol_class(self, service)
