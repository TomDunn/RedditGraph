#!/usr/bin/env python2.7

import argparse
import time
import sys
from uuid import uuid4

from twitter import TwitterHTTPError, TwitterError

from models import *
from tasks import task_map
from helpers.Twitter import t as tweeter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('task', help='A task to run')
    parser.add_argument('--no_notify', action='store_true')
    args = parser.parse_args()

    task_id = str(uuid4())[0:3]
    update = lambda s: notify("@%s #%s_%s %s" % ('ThomasDunn4', args.task, task_id, s)) or log_message(s)
    if args.no_notify:
        update = lambda s: log_message(s)

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
    status = "Time taken: %02d:%02d:%02d" % (hours, mins, secs)

    if finish_time - start_time >= 120.0:
        update(status)

def log_message(message):
    print message

def notify(message):
    try:
        tweeter.statuses.update(status=message[0:139])
    except (TwitterHTTPError, TwitterError) as twitter_exception:
        print "ERROR", "TWITTER", str(twitter_exception)

if __name__ == '__main__':
    main()
