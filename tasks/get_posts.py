from db import Session
from models.Post import Post
from helpers.RFactory import r

def main(notify):
    session = Session()
    gen = r.get_subreddit('all').get_top(limit=10000)

    start = session.query(Post).count()
    notify("Getting posts, initial count: %d" % start)

    for post in gen:
        p = Post()
        p.update_from_praw(post)
        session.merge(p)

        if (len(session.dirty) == 100):
            session.commit()

    session.commit()

    diff = session.query(Post).count() - start
    notify("Added %d posts" % diff)
