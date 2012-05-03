"""Aysyncore dispatcher for a Notary query"""

from HTTP_dispatcher import HTTP_dispatcher

class Notary_dispatcher(HTTP_dispatcher):

    def __init__(self, notary, service, map=None):
        self.protocol = notary.get_protocol(service)
        HTTP_dispatcher.__init__(self, self.protocol.get_url(), map=map)

    def get_response(self):
        """Return NotaryResponse instance"""
        response_fd = HTTP_dispatcher.get_response(self)
        data = response_fd.read()
        response = self.protocol.parse_response(data)
        return response
