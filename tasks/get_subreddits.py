from db import Session
from models.Subreddit import Subreddit
from helpers.RFactory import r

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
