from time import sleep

class ExponentialBackoff():
    def __init__(self, base=2, exp=1):
        self.base   = base
        self.exp    = exp

    def __call__(self):
        sleep_time = self.base ** self.exp
        print "sleeping: ", sleep_time
        self.exp += 1
        sleep(sleep_time)
