#!/usr/bin/env python2.7

import argparse
import time
import sys
from uuid import uuid4

from twitter import TwitterHTTPError, TwitterError

from tasks import task_map
from helpers.Twitter import t as tweeter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('task', help='A task to run')
    args = parser.parse_args()
    update = lambda s: notify("@%s #%s_%s %s" % ('ThomasDunn4', args.task, str(uuid4())[0:3], s))

    module =  __import__(task_map[args.task])

    start_time = time.time()

    try:
        getattr(module, args.task).main(notify=update)
    except:
        e = sys.exc_info()[0]
        status = "E: %s" % str(e)
        update(status)
        raise

    finish_time = time.time()

    mins, secs  = divmod(finish_time - start_time, 60)
    hours, mins = divmod(mins, 60)
    status = "@%s #%s has finished. Time taken: %02d:%02d:%02d" % ('ThomasDunn4', args.task, hours, mins, secs)

    if finish_time - start_time >= 120.0:
        update(status)

def notify(message):
    try:
        tweeter.statuses.update(status=message[0:139])
    except (TwitterHTTPError, TwitterError) as twitter_exception:
        print "ERROR", "TWITTER", str(twitter_exception)

if __name__ == '__main__':
    main()
