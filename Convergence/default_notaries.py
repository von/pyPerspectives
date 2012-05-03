"""Default Notaries"""

import pkgutil
import StringIO

from NotaryParser import NotaryParser

def default_notaries():
    """Return the default Notaries"""
    parser = NotaryParser()
    data = pkgutil.get_data("Convergence", "conf/thoughtcrime.notary")
    return parser.parse_stream(StringIO.StringIO(data))
