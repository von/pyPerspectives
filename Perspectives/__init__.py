# Make these classes available via 'from Perspectives import ...'
from Exceptions import PerspectivesException
from Exceptions import FingerprintException
from Exceptions import NotaryException
from Exceptions import NotaryResponseException
from Exceptions import NotaryUnknownServiceException
from Exceptions import NotaryResponseBadSignature
from Fingerprint import Fingerprint
from Notary import Notary
from Notaries import Notaries
from NotaryParser import NotaryParser
from NotaryResponse import NotaryResponse
from NotaryResponse import NotaryResponseKey
from NotaryResponse import NotaryResponseTimeSpan
from NotaryResponse import ServiceKey
from NotaryResponses import NotaryResponses
from Protocol import Protocol
from Service import Service, ServiceType

# Avoid warnings about lack of defined handlers
# http://docs.python.org/howto/logging.html#library-config
import logging

# NullHandler not in Python < 2.7
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger("Perspectives").addHandler(NullHandler())
