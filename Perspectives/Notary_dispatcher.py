"""Aysyncore dispatcher for a Notary query"""

from HTTP_dispatcher import HTTP_dispatcher
from NotaryResponse import NotaryResponse

class Notary_dispatcher(HTTP_dispatcher):

    response_class = NotaryResponse

    def get_response(self):
        """Return NotaryResponse instance"""
        response_fd = HTTP_dispatcher.get_response(self)
        data = response_fd.read()
        response = self.response_class(data)
        return response
