import datetime
import time
from functools import wraps

class RateLimiter(object):

    def __init__(self, max_rate, throttle_stop=False):
        # Dict of max number of requests of the API rate limit for each source
        self.max_rate = max_rate
        # Dict of duration of the API rate limit for each source
        self.throttle_stop = throttle_stop
        # the time window for every source
        self.window = 10
        now = datetime.datetime.now()
        # Initialization
        self.next_reset_at = now + datetime.timedelta(seconds=self.window)
        self.num_requests = 0

    def request(self, source):
        now = datetime.datetime.now()
        # <--- MAKE API CALLS ---> #
        self.num_requests += 1
        # reset the count if the period passed
        if now > self.next_reset_at:
            self.num_requests = 0
            self.next_reset_at = now + datetime.timedelta(seconds=self.window)

        @wraps(source)
        def dummy():
            return 'the number of requests is:{}'.format(str(self.num_requests))

        # throttle request
        def halt(wait_time):
            time.sleep(wait_time)
            return dummy

        # if exceed max rate, need to wait
        if self.num_requests >= 2:
            return halt(10)
            # return halt(10)
        return source