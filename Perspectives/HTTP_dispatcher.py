"""HTTP_dispatcher: asyncore.dispatcher with HTTP/HTTPS support"""

# For some sites (e.g., https://githib.com) it can take a long time
# for the connection to be recognized as closed. I'm not sure if that
# is because the site isn't closing the connection and the
# HTTP_dispatcher needs to key off of the content being done, or the
# close just isn't percolating up.

import httplib
import logging
import socket
import StringIO
import sys
import urlparse

from ssl_dispatcher import ssl_dispatcher

class StringBuffer(StringIO.StringIO):
    def makefile(self, *args, **kw):
        return self
    def sendall(self, arg):
        self.write(arg)

class HTTP_dispatcher(ssl_dispatcher):
    """asyncore.dispatcher with HTTP/HTTPS support"""

    def __init__(self, url, method="GET", post_data=None, map=None):
        self.logger = logging.getLogger("Perspectives.HTTP_dispatcher")
        ssl_dispatcher.__init__(self, map=map)
        self.write_buffer = ""
        self.read_buffer = StringBuffer()
        self.amount_read = 0

        self.url = url
        self.parsed_url = urlparse.urlparse(url)
        if self.parsed_url.netloc.find(":") == -1:
            self.hostname = self.parsed_url.netloc
            self.port = 443 if self.parsed_url.scheme == "https" else 80
        else:
            self.hostname, port_str = self.parsed_url.netloc.split(":")
            self.port = int(port_str)
        address = (self.hostname, self.port)
        self.logger.debug('connecting to %s:%d' % (self.hostname,
                                                   self.port))
        
        path = urlparse.urlunparse((None, # Scheme
                                    None, # netloc
                                    self.parsed_url.path,
                                    self.parsed_url.params,
                                    self.parsed_url.query,
                                    self.parsed_url.fragment))
        http_conn = httplib.HTTPConnection(self.hostname)
        http_conn.sock = StringBuffer()
        http_conn.request(method,
                          path,
                          post_data
                          )
        request = http_conn.sock.getvalue()
        self.write_buffer = request
        self.logger.debug("%s: %s %s" % (self.hostname, method, path))

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(address)
        self.logger.debug("%s: initialized" % self.hostname)

    def handle_connect(self):
        self.logger.debug("%s: Connected" % self.hostname)
        if self.parsed_url.scheme == "https":
            self.logger.debug("%s: Starting SSL handshake" % self.hostname)
            self.start_ssl()
        
    def writable(self):
        return (len(self.write_buffer) > 0)

    def handle_write(self):
        sent = self.send(self.write_buffer)
        self.logger.debug("%s: wrote %d bytes" % (self.hostname, sent))
        self.write_buffer = self.write_buffer[sent:]

    def handle_read(self):
        data = self.recv(8192)
        self.read_buffer.write(data)
        self.amount_read += len(data)
        self.logger.debug("%s: read %d bytes" % (self.hostname, len(data)))

    def handle_close(self):
        self.logger.debug("%s: Closing" % self.hostname)
        self.close()

    def get_response(self):
        """Return the HTTPResponse

        Raises EOFError if no response received."""
        self.read_buffer.seek(0)
        if self.amount_read == 0:
            raise EOFError("Read zero bytes")
        self.logger.debug(
            "%s: Processing response of %d bytes" % (self.hostname,
                                                     self.amount_read))
        response = httplib.HTTPResponse(self.read_buffer)
        response.begin()  # Process the response
        return response

    def handle_error(self):
        type, value = sys.exc_info()[0:2]
        self.logger.error("%s: Error: %s" % (self.hostname, value))
        sys.exc_clear()
        self.close()
