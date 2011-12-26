#!/usr/bin/env python
"""Query Perspectives Notaries regarding a given server"""

import argparse
import logging
import sys

from Perspectives import default_notaries, \
    NotaryParser, Service, ServiceType

class Counter:
    """Count down to zero and then call a function."""

    def __init__(self, initial_value, onZeroCall, *onZeroCallArgs):
        self.value = initial_value
        self.func = onZeroCall
        self.func_args = onZeroCallArgs

    def decrement(self, *ignored):
        """Decrement our value, calling function if we hit zero.

        Extra arguments are ignored."""
        if self.value > 0:
            self.value -= 1
            if self.value == 0:
                self.func(*self.func_args)

def normal_query(notaries, service, output, args):
    responses = notaries.query(service, num=args.num_notaries)
    output_responses(responses, output, args)
    return(0)

def twisted_query(notaries, service, output, args):
    from twisted.internet import reactor
    deferreds = notaries.deferred_query(service, num=args.num_notaries)
    for deferred in deferreds:
        deferred.addCallback(output_response, output, args)
        deferred.addErrback(output_err, output, args)
    # Stop reactor when all responses received
    counter = Counter(len(deferreds), twisted_query_done, output)
    for deferred in deferreds:
        deferred.addBoth(counter.decrement)
    # ...or when timeout is reached
    reactor.callLater(args.timeout, twisted_query_timeout, deferreds, output)
    reactor.run()
    return(0)

def twisted_query_done(output):
    """Called at end of twisted callback chain to stop reactor."""
    from twisted.internet import reactor
    output.info("Query complete.")
    reactor.stop()

def twisted_query_timeout(deferreds, output):
    """Called if query times out."""
    for deferred in deferreds:
        deferred.cancel()

def output_response(response, output, args):
    output.info("Response from %s:" % response.notary)
    if args.output_raw:
        output.info(response.raw_response)
    else:
        output.info(response)

def output_err(err, output, args):
    msg = err.getErrorMessage()
    if not msg:
        msg = "Timed out"
    output.error("Error querying %s: %s\n" % (err.notary, msg))

def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    # Set up out output via logging module
    output = logging.getLogger("main")
    output.setLevel(logging.DEBUG)
    output_handler = logging.StreamHandler(sys.stdout)  # Default is sys.stderr
    # Set up formatter to just print message without preamble
    output_handler.setFormatter(logging.Formatter("%(message)s"))
    output.addHandler(output_handler)

    # Set up logging for Perspectives code as well
    perspectives_logger = logging.getLogger("Perspectives")
    perspectives_logger.setLevel(logging.DEBUG)
    perspectives_logger.addHandler(output_handler)

    # Argument parsing
    parser = argparse.ArgumentParser(
        description=__doc__, # printed with -h/--help
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    # Only allow one of debug/quiet mode
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument("-d", "--debug",
                                 action='store_const', const=logging.DEBUG,
                                 dest="output_level", default=logging.INFO,
                                 help="print debugging")
    verbosity_group.add_argument("-q", "--quiet",
                                 action="store_const", const=logging.WARNING,
                                 dest="output_level",
                                 help="run quietly")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    parser.add_argument("-n", "--num_notaries",
                        type=int, default=0,
                        help="specify number of notaries to query (0=All)",
                        metavar="num")
    parser.add_argument("-N", "--notaries-file",
                        type=str, default=None,
                        help="specify notaries file", metavar="filename")
    parser.add_argument("-o", "--timeout",
                        type=int, default=10,
                        help="specify timeout in seconds", metavar="seconds")
    parser.add_argument("-p", "--port", dest="service_port",
                        type=int, default=443,
                        help="specify service port", metavar="port")
    parser.add_argument("-r", "--raw",
                        dest="output_raw", action="store_const", const=True,
                        default=False,
                        help="output raw response")
    parser.add_argument("-t", "--type", dest="service_type",
                        type=int, default=ServiceType.SSL,
                        help="specify service type", metavar="type")
    parser.add_argument("-T", "--twisted",
                        default=False, action="store_true",
                        help="query using twisted")
    parser.add_argument('service_hostname', metavar='hostname',
                        type=str, nargs=1,
                        help='host about which to query')
    args = parser.parse_args()

    output_handler.setLevel(args.output_level)

    service = Service(args.service_hostname[0],
                      args.service_port,
                      args.service_type)

    if args.twisted:
        output.info("Using twisted version")
        query_func = twisted_query
    else:
        query_func = normal_query

    if args.notaries_file:
        output.debug("Reading notaries from %s" % args.notaries_file)
        notaries = NotaryParser().parse_file(args.notaries_file)
    else:
        output.debug("Using default notaries")
        notaries = default_notaries()
    output.debug("Have %d notaries" % len(notaries))

    query_func(notaries, service, output, args)
    
    return(0)

if __name__ == "__main__":
    sys.exit(main())

