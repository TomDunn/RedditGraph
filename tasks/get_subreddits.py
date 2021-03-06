from celery import chain
import praw

from db import Session
from helpers.RFactory import r
from models.Subreddit import Subreddit
from tasks.config.celery import celery

def main(notify):
    session = Session()
    gen = r.get_popular_subreddits(limit=30000)

    count = session.query(Subreddit).count()
    notify("Getting subs, initial count: %d" % count)

    for praw_subreddit in gen:
        count += 1

        subreddit = Subreddit.get_or_create(session, praw_subreddit.display_name)
        subreddit.update_from_praw(praw_subreddit)

        session.add(subreddit)

    session.commit()
    notify("Now have %d" % count)

@celery.task
def get_subreddit(display_name):
    try:
        subreddit = r.get_subreddit(display_name)
        subreddit.title # force praw to load
        return subreddit._json_data
    except praw.errors.InvalidSubreddit:
        return None
    except praw.requests.exceptions.HTTPError as e:
        if Util.is_400_exception(e):
            return None
        else:
            return False
