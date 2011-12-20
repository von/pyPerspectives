"""Utilities for testing"""

import os.path

my_path = os.path.dirname(os.path.abspath( __file__ ))
notary_file = os.path.join(my_path, "./http_notary_list.txt")

def test_notaries():
    """Return test Notaries"""
    from Perspectives import NotaryParser
    parser = NotaryParser()
    notaries = parser.parse_file(notary_file)
    return notaries

def test_service():
    """Return test Service"""
    from Perspectives import Service
    return Service("test.example.com", 443)

def test_responses():
    """Return array of responses as strings"""
    filenames = [
        "response.1",
        "response.2",
        "response.3",
        "response.4"
        ]
    responses = []
    for filename in filenames:
        with open(os.path.join(my_path, filename)) as f:
            responses.append("".join(f.readlines()))
    return responses

def load_response(filename):
    """Load the response given by the filename"""
    with open(os.path.join(my_path, filename)) as f:
            response_string = "".join(f.readlines())
    return response_string

def create_NotaryResponse():
    """Return a NotaryResponse instance"""
    from Perspectives import NotaryResponse
    from Perspectives import Protocol
    from Perspectives import Service, ServiceType
    notaries = test_notaries()
    notary = notaries.find_notary("cmu.ron.lcs.mit.edu")
    service = Service("www.citibank.com",
                      443,
                      ServiceType.SSL)
    protocol = Protocol(notary, service)
    response_string = load_response("response.1")
    response = protocol.parse_response(response_string)
    return response
