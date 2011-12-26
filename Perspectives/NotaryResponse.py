"""NotaryResponse: Response from a Notary"""

import base64
import struct
import time
import xml.dom.minidom

from Exceptions import NotaryResponseException
from Fingerprint import Fingerprint

class NotaryResponse:
    """Response from a Notary"""

    # signature type mappings
    SIG_TYPE_MAPPINGS = {
        # Perspectives sig_type
        u"rsa-md5" : "md5"
        }

    def __init__(self, notary, version, keys, sig_type, sig, raw_response):
        """Create a NotaryResponse instance"""
        self.notary = notary
        self.version = version
        self.keys = keys
        self.sig_type = self.SIG_TYPE_MAPPINGS[sig_type] \
            if self.SIG_TYPE_MAPPINGS.has_key(sig_type) else sig_type
        self.sig = sig
        self.raw_response = raw_response

    def bytes(self):
        """Return as bytes for signature verification

        Bytes is concatenated key data in reverse order"""
        data = bytearray()
        key_data = [key.bytes() for key in self.keys]
        key_data.reverse()
        for kd in key_data:
            data.extend(kd)
        return data

    def last_key_seen(self):
        """Return most recently seen key"""
        return max(self.keys, key=lambda k: k.last_timestamp())

    def key_at_time(self, time):
        """Get key seen at time (expressed in seconds)

        Returns None if no key known at given time."""
        for key in self.keys:
            for span in key.timespans:
                if (span.start <= time) and (span.end >= time):
                    return key
        return None

    def key_change_times(self):
        """Return list of all times the key changed"""
        return reduce(lambda a,b: a + b,
                      [key.change_times() for key in self.keys])

    def __str__(self):
        s = "Notary response from %s\n" % self.notary
        s += "\tVersion: %s Signature type: %s\n" % (self.version,
                                                     self.sig_type)
        s += "\tSig: %s\n" % (base64.standard_b64encode(self.sig))
        for key in self.keys:
            s += str(key)
        return s

class ServiceKey:
    """Representation of a service's key"""
    def __init__(self, type, fingerprint):
        """Create a instance of a service key with given type and fingerprint.

        Type is a string as returned in a Notary response.
        Fingerprint is a Fingerprint instance."""
        self.type = type
        self.fingerprint = fingerprint

    @classmethod
    def from_string(cls, type, str):
        """Create a ServiceKey instance from a string such as:
        93:cc:ed:bb:b9:84:42:fc:da:13:49:6a:89:95:50:28"""
        fingerprint = Fingerprint.from_string(str)
        return cls(type, fingerprint)

    def __eq__(self, other):
        return ((self.type == other.type) and
                (self.fingerprint == other.fingerprint))

    def __str__(self):
        s = "Fingerprint: %s type: %s\n" % (self.fingerprint, self.type)
        return s
     
class NotaryResponseKey(ServiceKey):
    """Representation of a Key in a Notary Response"""

    def __init__(self, type, fingerprint, timespans):
        ServiceKey.__init__(self, type, fingerprint)
        self.timespans = timespans

    def bytes(self):
        """Return as bytes for signature verification

        Data is for each key:
            Number of timespans as 2-byte tuple
            0, 16, 3  -- I don't know what these are
            Fingerprint
            Data for each timespan
        """
        data = bytearray(struct.pack("BB",
                                     (len(self.timespans) >> 8) & 255,
                                     len(self.timespans) & 255))
        # I don't know what these three values are
        data.extend(struct.pack("BBB", 0, 16, 3))
        data.extend(self.fingerprint.data)
        data.extend(b"".join([t.bytes() for t in self.timespans]))
        return data

    def change_times(self):
        """Return an list of all timespan end times"""
        return [t.end for t in self.timespans] + [t.start for t in self.timespans]

    def last_timestamp(self):
        """Return the last time we saw this key"""
        return max([ts.end for ts in self.timespans])

    def __str__(self):
        s = ServiceKey.__str__(self)
        for t in self.timespans:
            s += str(t) + "\n"
        return s

class NotaryResponseTimeSpan:
    """Time span (Timestamp) from a Notary response"""

    def __init__(self, start, end):
        """Create NotaryResponseTimeSpan from dom"""
        self.start = start
        self.end = end

    def bytes(self):
        """Return as bytes for signature verification

        Data is start as 4 byte value concatenated with end as 4 byte value"""
        start_bytes = struct.pack("BBBB",
                                  (self.start >> 24) & 255,
                                  (self.start >> 16) & 255,
                                  (self.start >> 8) & 255,
                                  self.start & 255)                    
        end_bytes = struct.pack("BBBB",
                                (self.end >> 24) & 255,
                                (self.end >> 16) & 255,
                                (self.end >> 8) & 255,
                                self.end & 255)                    
        return b"".join([start_bytes, end_bytes])

    def __str__(self):
        return "%s - %s" % (time.ctime(self.start), time.ctime(self.end))
