from db import Session
from models.Post import Post
from helpers.RFactory import r

def main(notify):
    session = Session()
    gen = r.get_subreddit('all').get_top(limit=1000)

    start = session.query(Post).count()
    notify("Getting posts, initial count: %d" % start)
    count = 0

    for post in gen:
        try: 
            count += 1

            p = Post()
            p.update_from_praw(post)
            p = session.merge(p)

            session.add(p)

            if (count % 50 == 0):
                session.commit()

        except AttributeError:
            pass

    session.commit()

    diff = session.query(Post).count() - start
    notify("Added %d posts" % diff)
