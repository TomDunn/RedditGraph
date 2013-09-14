from db import Session
from models.Subreddit import Subreddit
from helpers.RFactory import r

def main(notify):
    session = Session()
    gen = r.get_popular_subreddits(limit=2000)

    start = session.query(Subreddit).count()
    count = 0
    notify("Getting subs, initial count: %d" % start)

    for sub in gen:
        try: 
            count += 1

            s = Subreddit()
            s.update_from_praw(sub)
            session.merge(s)

            if (count % 100 == 0):
                print "Saving"
                session.commit()

        except AttributeError as e:
            print e
            print sub.id, sub.title

    session.commit()

    diff = session.query(Subreddit).count() - start
    notify("Added %d subs" % diff)
