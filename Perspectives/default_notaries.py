"""Default Notaries"""

import pkgutil
import StringIO

from NotaryParser import NotaryParser

def default_notaries():
    """Return the default Notaries"""
    parser = NotaryParser()
    data = pkgutil.get_data("Perspectives", "conf/http_notary_list.txt")
    return parser.parse_stream(StringIO.StringIO(data))
