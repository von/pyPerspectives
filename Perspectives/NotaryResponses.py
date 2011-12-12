"""NotaryResponses: List of NotaryResponse instances"""

import logging
import time

class NotaryResponses(list):
    """Wrapper around a list of NotaryResponse instances"""

    logger = logging.getLogger("Perspectives.NotaryResponses")

    def quorum_duration(self, cert_fingerprint, quorum, stale_limit):
        """Return the quorum duration of the given certificate in seconds.

        Quorum duration is the length of time at least quorum Notaries
        believe the certificate was valid.

        quorum specifies the number of notaries needed to make quorum

        stale_limit: any response without a seen key fresher than this
        limit is ignored inside this limit. I.e. a notary with a stale
        response does not count towards quorum inside this period.
        """
        if quorum > len(self):
            return(0)

        # Find the response with the last seen key with the oldest
        # time that is not older than stale_limit.
        now = int(time.time())
        stale_time_cutoff = now - stale_limit
        valid_responses = [r for r in self if r is not None]
        last_seen_key_times = [r.last_key_seen().last_timestamp() for r in valid_responses]
        non_stale_response_times = filter(lambda t: t > stale_time_cutoff,
                                          last_seen_key_times)
        if len(non_stale_response_times) == 0:
            self.logger.debug("No non-stale responses")
            return(0)
        oldest_response_time = min(non_stale_response_times)
        self.logger.debug("Oldest response time is %s" % (time.ctime(oldest_response_time)))

        # Get list of all times we had a key change
        key_change_times = reduce(lambda a,b: a + b,
                                  [r.key_change_times()
                                   for r in valid_responses])
        # We ignore all key_change_times after the oldest_response_time
        key_change_times = filter(lambda t: t <= oldest_response_time,
                                  key_change_times)

        # Make list of change times go from newest to oldest
        key_change_times.sort()
        key_change_times.reverse()

        first_valid_time = None
        for change_time in key_change_times:
            self.logger.debug("Checking time %s" % (time.ctime(change_time)))
            agreement_count = self.key_agreement_count(cert_fingerprint,
                                                       change_time)
            if agreement_count >= quorum:
                first_valid_time = change_time
                self.logger.debug("Quorum made with %s notaries" % (agreement_count))
            else:
                self.logger.debug("Not enough notaries to make quorum (%s)" % (agreement_count))
                break
        if first_valid_time is None:
            return 0  # No quorum_duration
        return now - first_valid_time

    def key_agreement_count(self, cert_fingerprint, check_time=None):
        """How many notaries agree given certificate was valid at given time?

        If check_time == None, then check for last seen key."""
        count = 0
        for response in self:
            if response is not None:
                if check_time is None:
                    seen_key = response.last_key_seen()
                else:
                    seen_key = response.key_at_time(check_time)
                if (seen_key is not None) and \
                        (seen_key.fingerprint == cert_fingerprint):
                    count += 1
        return count
