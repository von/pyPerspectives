"""Notaries: List of Notary instances"""
import httplib
import logging
import random

from Notary import Notary
from Exceptions import NotaryException
from NotaryResponses import NotaryResponses
import timed_asyncore

class Notaries(list):
    """Class for representing the set of trusted Notaries"""

    NotaryClass = Notary

    def __init__(self):
        self.logger = logging.getLogger("Perspectives.Notary")
        list.__init__(self)

    def query(self, service, num=0, timeout=10):
        """Query Notaries and return NotaryResponses instance

        For any Notary not responding, a None will be in the array.

        num specifies the number of Notaries to query. If 0, all notaries
        are queried.

        timeout is the timeout in seconds"""
        if num == 0:
            to_query = self
        else:
            if num > len(self):
                raise ValueError("Too many notaries requested (%s > %s)" % (num, len(self)))
            to_query = random.sample(self, num)
        responses = NotaryResponses()
        dispatchers = []
        # Use own map here for thread safety
        map = {}
        for notary in to_query:
            self.logger.debug("Querying %s about %s..." % (notary, service))
            dispatchers.append((notary, notary.get_dispatcher(service, map)))
        self.logger.debug("Calling asyncore.loop()")
        timed_asyncore.loop_with_timeout(timeout=timeout, map=map)
        self.logger.debug("asyncore.loop() done.")
        for notary, dispatcher in dispatchers:
            try:
                self.logger.debug("Parsing response from %s" % notary)
                response = dispatcher.get_response()
                self.logger.debug("Response from %s parsed" % notary)
                responses.append(response)
            except EOFError as e:
                self.logger.error("Failed to get response from %s: %s" % (notary, str(e)))
                responses.append(None)
            except httplib.BadStatusLine as e:
                self.logger.error("Failed to parse response from %s, bad status: %s" % (notary, e))
                responses.append(None)
            except NotaryException as e:
                self.logger.error("Error validating response from %s: %s" % (notary, e))
                responses.append(None)
            except Exception as e:
                self.logger.exception("Unknown error handling response from %s: %s" % (notary, e))
                responses.append(None)
        return responses

    def deferred_query(self, service, num=0):
        """Make a deferred twisted query for each protocol returning a list of Deferred.

        For CallBacks, the argument will be a NotaryResponse instance.
        For ErrBacks, the Failure will have a notary attribute being the Notary.

        Returns a list of Deferred instead of a DeferredList to allow for timeouts.
"""
        if num == 0:
            to_query = self
        else:
            if num > len(self):
                raise ValueError(
                    "Too many notaries requested (%s > %s)" % (num, len(self)))
            to_query = random.sample(self, num)
        deferreds = [n.defered_query(service) for n in to_query]
        return deferreds

    @classmethod
    def _deferred_query_callback(cls, list):
        responses = NotaryResponses([])
        for success, response in list:
            if success:
                responses.append(response)
        return responses

    def find_notary(self, hostname, port=None):
        """Find notary inlist.

        hostname must match. If port is not None, it must match too.

        Returns None if notary is not found."""
        for notary in self:
            if notary.hostname != hostname:
                continue
            if (port is not None) and (notary.port != port):
                continue
            return notary
        # Failure
        return None

    def __str__(self):
        return "[" + ",".join([str(n) for n in self]) + "]"
