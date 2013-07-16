import praw

from db import Session
from models.Subreddit import Subreddit
from helpers.DBIterator import DBIterator
from helpers.RFactory import r

def main(notify):

    session = Session()
    total = session.query(Subreddit).count()
    count = 0

    notify("starting update of %d subs" % total)

    query   = session.query(Subreddit).order_by("scraped_time asc")
    dbi     = DBIterator(query=query, use_offset=None)

    for subreddit in dbi.results_iter():

        count += 1

        try:
            subreddit.update_from_praw(r.get_subreddit(subreddit.url.split('/')[2]))
            session.add(subreddit)

        except (praw.requests.exceptions.HTTPError, praw.errors.InvalidSubreddit) as e:
            print "ERROR", str(e)
            subreddit.touch()
            session.add(subreddit)

        if count % 2000 == 0 and notify is not None:
            notify("at %d of %d" % (count, total))

        if count % 10 == 0:
            session.commit()

    session.commit()
