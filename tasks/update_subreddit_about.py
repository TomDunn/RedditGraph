import praw
from sqlalchemy.sql.expression import asc

from db import Session
from models.Subreddit import Subreddit
from models.DiscoveredSub import DiscoveredSub

def main(notify):

    r = praw.Reddit(user_agent='subreddit info grabber 1.0 by u/lungfungus')
    r.config.log_requests = 2
    session = Session()
    total = session.query(Subreddit).count()
    count = 0

    if notify is not None:
        notify("starting update of %d subs" % total)

    updated = set()

    while count < total:
        for subreddit in session.query(Subreddit).order_by(asc(Subreddit.scraped_time)).limit(20):

            count += 1
            updated.add(subreddit.id)

            try:

                subreddit.update_from_praw(r.get_subreddit(subreddit.url.split('/')[2]))
                session.add(subreddit)

            except (praw.requests.exceptions.HTTPError, praw.errors.InvalidSubreddit) as e:
                print "ERROR", str(e)
                subreddit.touch()
                session.add(subreddit)

            if count % 2000 == 0 and notify is not None:
                notify("at %d of %d" % (count, total))

            session.commit()

    print "updated is of length %d" % len(updated)
