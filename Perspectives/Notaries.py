"""Notaries: List of Notary instances"""
import httplib
import logging
import pkgutil
import random
import StringIO

from Notary import Notary
from Exceptions import NotaryException
from NotaryResponse import NotaryResponse
from NotaryResponses import NotaryResponses
import timed_asyncore

class Notaries(list):
    """Class for representing the set of trusted Notaries"""

    NotaryClass = Notary

    def __init__(self):
        self.logger = logging.getLogger("Perspectives.Notary")
        list.__init__(self)

    @classmethod
    def default(cls):
        """Return the default Notaries"""
        data = pkgutil.get_data("Perspectives", "conf/http_notary_list.txt")
        return cls.from_stream(StringIO.StringIO(data))

    @classmethod
    def from_file(cls, file_path):
        """Return Notaries described in file.

        See from_stream() for expected format."""
        with file(file_path, "r") as f:
            notaries = cls.from_stream(f)
        return notaries

    @classmethod
    def from_stream(cls, stream):
        """Return Notaries described in given stream.

        Expected format for each Notary is:
        # Lines starting with '#' are comments and ignored
        <hostname>:<port>
        -----BEGIN PUBLIC KEY-----
        <multiple lines of Base64-encoded data>
        -----END PUBLIC KEY----
        """
        notaries = cls()
        while True:
            notary = cls.NotaryClass.from_stream(stream)
            if notary is None:  # EOF
                break
            else:
                notaries.append(notary)
        return notaries

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
                response = dispatcher.get_response()
                self.logger.debug("Validating response from %s" % notary)
                notary.verify_response(response, service)
                self.logger.debug("Response signature verified")
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
                self.logger.error("Unknown error handling response from %s: %s" % (notary, e))
                responses.append(None)
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
