"""Versions of Perspectives classess that use twisted"""

import logging

import twisted.internet
from twisted.web.client import getPage
from twisted.web.http_headers import Headers

from . import Notary, NotaryResponse, NotaryResponses, Notaries

class TwistedNotary(Notary):
    def defered_query(self, service, reactor=twisted.internet.reactor):
        """Query Notary. Returns a Deferred instance."""
        url = self.get_url(service)
        self.logger.debug("%s: defered_query" % self.hostname)
        d = getPage(url)
        d.addCallback(self._parse_response)
        return d

    def _parse_response(self, response):
        """Callback that converts raw XML into a NotaryResponse object"""
        self.logger.debug("%s: defered response" % self.hostname)
        return NotaryResponse(response)

class TwistedNotaries(Notaries):

    NotaryClass = TwistedNotary

    def defered_query(self, service, num=0, timeout=10,
                      reactor=twisted.internet.reactor):
        """Query Notaries. Returns a Deferred instance."""
        if num == 0:
            to_query = self
        else:
            if num > len(self):
                raise ValueError("Too many notaries requested (%s > %s)" % (num, len(self)))
            to_query = random.sample(self, num)
        self.logger.debug("Starting defered queries to %d notaries" % len(to_query))
        my_deferred = twisted.internet.defer.Deferred()
        state = _TwistedNotariesQuery(my_deferred, timeout, reactor)
        for notary in to_query:
            d = notary.defered_query(service, reactor)
            state.add_defered(d)
        return my_deferred

class _TwistedNotariesQuery:
    """State for a in progress Notaries.defered_query()

    Created with a defered which will be called with NotaryResponses instance"""

    def __init__(self, defered, timeout=None, reactor=twisted.internet.reactor):
        """defered is the Deferred that will be called when query complete"""
        self.logger = logging.getLogger("Perspectives.TwistedNotariesQuery")
        self.defered = defered
        self.defereds = []
        self.responses = []
        if timeout:
            self.logger.debug("Query timeout is %d seconds" % timeout)
            self.timeout = reactor.callLater(timeout, self.respond)
        else:
            self.timeout = None

    def add_defered(self, d):
        """Add a defered to monitor."""
        self.defereds.append(d)
        d.addCallback(self.handle_response)
        d.addErrback(self.handle_error)

    def handle_response(self, response):
        """Callback to handle a successful response"""
        self.responses.append(response)
        if len(self.responses) == len(self.defereds):
            self.respond()

    def handle_error(self, failure):
        """Callback to handle an error in response"""
        self.logger.debug("Caught failure")
        self.handle_response(None)  # We return a None for response

    def respond(self):
        """Wrap up and call our Deferred."""
        self.logger.debug("Query done. Responding.")
        if self.timeout:
            self.timeout.cancel()
        for d in self.defereds:
            d.cancel()
        self.defered.callback(NotaryResponses(self.responses))
        self.logger.debug("Response done.")

    def timeout(self):
        """Timeout reached. Wrap it up."""
        self.logger.debug("Query timed out.")
        self.response()

