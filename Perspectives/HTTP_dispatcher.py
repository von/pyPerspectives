"""HTTP query client based on asyncore

Adapted from:

http://blog.doughellmann.com/2009/03/pymotw-asyncore.html

and

http://pythonwise.blogspot.com/2010/02/parse-http-response.html
"""

import asyncore
from httplib import HTTPResponse
import logging
import socket
from StringIO import StringIO
import sys
import urlparse

class ResponseBuffer(StringIO):
    def makefile(self, *args, **kw):
        return self

class HTTP_dispatcher(asyncore.dispatcher_with_send):

    def __init__(self, url, map=None):
        self.url = url
        self.logger = logging.getLogger("Perspectives.HTTP_dispatcher")
        self.parsed_url = urlparse.urlparse(url)
        if self.parsed_url.netloc.find(":") == -1:
            self.hostname = self.parsed_url.netloc
            self.port = 80
        else:
            self.hostname, port_str = self.parsed_url.netloc.split(":")
            self.port = int(port_str)
        asyncore.dispatcher_with_send.__init__(self, map=map)
        self.read_buffer = ResponseBuffer()
        self.amount_read = 0
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (self.hostname, self.port)
        self.logger.debug('connecting to %s', address)
        self.connect(address)

    def handle_connect(self):
        self.logger.debug("%s: Connected. Sending GET command." % self.hostname)
        self.send("GET %s HTTP/1.0\r\n\r\n" % (self.url))

    def handle_close(self):
        self.logger.debug("%s: Closed." % self.hostname)
        self.close()
    
    def readable(self):
        return True

    def handle_read(self):
        data = self.recv(8192)
        self.logger.debug("%s: Read %d bytes" % (self.hostname, len(data)))
        self.read_buffer.write(data)
        self.amount_read += len(data)

    def get_response(self):
        """Return the parse XML response.

        If no data was read, raises EOFError."""
        self.read_buffer.seek(0)
        if self.amount_read == 0:
            raise EOFError("Read zero bytes") 
        self.logger.debug("%s: Processing response of %d bytes" % (self.hostname, self.amount_read))
        response = HTTPResponse(self.read_buffer)
        response.begin()  # Process the response
        return response

    def handle_error(self):
        type, value = sys.exc_info()[0:2]
        self.logger.error("%s: Error: %s" % (self.hostname,
                                                 value))
        sys.exc_clear()
        self.close()
