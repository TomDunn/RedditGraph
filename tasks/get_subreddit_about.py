#!/usr/bin/env python2.7

import json
import os
import sys

from twitter import TwitterHTTPError, TwitterError
import praw

from helpers.Twitter import t as tweeter
from db import Session
from models.Subreddit import Subreddit
from models.DiscoveredSub import DiscoveredSub

def main():
    r = praw.Reddit(user_agent='subreddit info grabber 1.0 by u/lungfungus')
    r.config.log_requests = 2
    session = Session()
    count = session.query(Subreddit).count()

    for sub_stub in session.query(DiscoveredSub).filter(DiscoveredSub.status == 'NONE'):

        sub_name = sub_stub.url.split('/')[2].strip()
        count += 1

        try:
            if sub_name == 'random' or sub_name == None or sub_name == '':
                raise praw.errors.InvalidSubreddit("random or None")

            s = r.get_subreddit(sub_name)
            sub = Subreddit()
            sub.update_from_praw(s)
            sub_stub.status = "OK"

            session.add(sub)
            session.add(sub_stub)

        except ValueError as e:
            print "ERROR", str(e)
            sub_stub.status = "E_RETRY"
            session.add(sub_stub)
        except praw.requests.exceptions.HTTPError as e:
            print "ERROR", str(e)
            if "client error" in e.message.lower():
                sub_stub.status = "E_NO_RETRY"
            else:
                sub_stub.status = "E_RETRY"
            session.add(sub_stub)
        except praw.errors.InvalidSubreddit as e:
            print "ERROR", str(e)
            sub_stub.status = "E_NO_RETRY"
            session.add(sub_stub)

        if count % 25 == 0:
            print "FINISHED %d subreddits" % count

        session.commit()

        if count % 2000 == 0:
            try:
                tweeter.statuses.update(status="@ThomasDunn4 #SubExpander is at %d" % count)
            except (TwitterHTTPError, TwitterError) as e:
                print "ERROR", "TWITTER", str(e)

    if len(session.dirty) > 0:
        session.commit()
