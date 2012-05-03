#!/usr/bin/env python
"""ssl_dispatcher: dispatcher with ssl support

Much taken from:
http://bugs.python.org/file20752/asyncore_ssl_v1.patch

"""
import asyncore
import logging
import ssl
import socket

# Enum for SSL connection state (indepedent of socket state)
SSL_STATE = type('SSLState', (), {
    "DISCONNECTED":0,
    "CONNECTING":1,  # Doing SSL Handshake
    "ESTABLISHED":2,
    "DISCONNECTING":3,
    })


class ssl_dispatcher(asyncore.dispatcher):
    """asyncore.dispatcher with ssl support"""

    _state = SSL_STATE.DISCONNECTED

    # Flag to indicate we should close after SSL shutdown completes
    _close_on_ssl_shutdown = False

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("Perspectives.HTTP_dispatcher")
        self.logger.debug("ssl_dispatcher initializing")
        asyncore.dispatcher.__init__(self, *args, **kwargs)
        
    def start_ssl(self):
        """Start SSL connection."""
        if self._state != SSL_STATE.DISCONNECTED:
            raise ValueError(
                "Tried to start already established SSL connection")
        self.logger.debug("Starting SSL handshake")
        ssl_socket = ssl.wrap_socket(self.socket,
                                     do_handshake_on_connect=False)
        self.set_socket(ssl_socket)
        self._state = SSL_STATE.CONNECTING
        self._do_ssl_handshake()  # Kick things off

    def handle_read_event(self):
        if self._state == SSL_STATE.CONNECTING:
            self._do_ssl_handshake()
        elif self._state == SSL_STATE.DISCONNECTING:
            self.ssl_shutdown()
        else:
            asyncore.dispatcher.handle_read_event(self)

    def handle_write_event(self):
        if self._state == SSL_STATE.CONNECTING:
            self._do_ssl_handshake()
        elif self._state == SSL_STATE.DISCONNECTING:
            self.ssl_shutdown()
        else:
            asyncore.dispatcher.handle_write_event(self)

    def send(self, data):
        try:
            return asyncore.dispatcher.send(self, data)
        except ssl.SSLError as err:
            if err.args[0] in (ssl.SSL_ERROR_EOF,
                               ssl.SSL_ERROR_ZERO_RETURN):
                return 0
            raise

    def recv(self, buffer_size):
        try:
            return asyncore.dispatcher.recv(self, buffer_size)
        except ssl.SSLError as err:
            if err.args[0] in (ssl.SSL_ERROR_EOF,
                               ssl.SSL_ERROR_ZERO_RETURN):
                self.handle_close()
                return ''
            if err.args[0] in (ssl.SSL_ERROR_WANT_READ,
                               ssl.SSL_ERROR_WANT_WRITE):
                return ''
            raise

    def close(self):
        # ssl_shutdown will presumably take a few roundtrips here.
        if self._state == SSL_STATE.ESTABLISHED:
            self._close_on_ssl_shutdown = True
            self.ssl_shutdown()
        if self._state == SSL_STATE.DISCONNECTED:
            return asyncore.dispatcher.close(self)
    
    def ssl_shutdown(self):
        """Tear down SSL layer switching back to a clear text connection."""
        if self._state == SSL_STATE.DISCONNECTED:
            raise ValueError("not using SSL")
        self._state = SSL_STATE.DISCONNECTING
        try:
            self.socket = self.socket.unwrap()
        except ssl.SSLError as err:
            if err.args[0] in (ssl.SSL_ERROR_WANT_READ,
                               ssl.SSL_ERROR_WANT_WRITE):
                return
            elif err.args[0] == ssl.SSL_ERROR_SSL:
                pass
            else:
                raise
        except socket.error as err:
            # Any "socket error" corresponds to a SSL_ERROR_SYSCALL
            # return from OpenSSL's SSL_shutdown(), corresponding to
            # a closed socket condition. See also:
            # http://www.mail-archive.com/openssl-users@openssl.org/msg60710.html
            pass
        self._state = SSL_STATE.DISCONNECTED
        self.handle_ssl_shutdown()
        if self._close_on_ssl_shutdown:
            # We were shutting down SSL because close() was called, now that
            # we are done doing so, return to it.
            self.close()

    def handle_ssl_established(self):
        """Called when the SSL handshake has completed."""
        self.log_info('unhandled handle_ssl_established event', 'warning')

    def handle_ssl_shutdown(self):
        """Called when SSL shutdown() has completed"""
        self.log_info('unhandled handle_ssl_shutdown event', 'warning')

    # --- internals

    def _do_ssl_handshake(self):
        """Kick off another handshake message"""
        try:
            self.socket.do_handshake()
            # No exception -> we are done with handshake
        except ssl.SSLError as err:
            if err.args[0] in (ssl.SSL_ERROR_WANT_READ,
                               ssl.SSL_ERROR_WANT_WRITE):
                return
            elif err.args[0] == ssl.SSL_ERROR_EOF:
                return self.handle_close()
            raise
        else:
            self._state = SSL_STATE.ESTABLISHED
            self.handle_ssl_established()

