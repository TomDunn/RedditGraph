from praw.objects import Subreddit

from db import Session
from helpers.RFactory import r
from models.Post import Post
from models.Subreddit import Subreddit
from models.User import User
from models.Util import Util
from tasks.config.celery import celery

def main(notify):
    session = Session()
    gen = r.get_subreddit('all').get_top(limit=3000)

    start = session.query(Post).count()
    notify("Getting posts, initial count: %d" % start)
    count = 0

    for post in gen:
        count += 1

        p = Post.get_or_create(session, post.id)
        p.update_from_praw(post)

        author_name = Util.patch_author(post.author)
        Util.update_user(User, p, session, author_name)
        Util.update_subreddit(Subreddit, p, session, post.subreddit.display_name)

        session.add(p)
        session.commit()

    diff = session.query(Post).count() - start
    notify("Added %d posts" % diff)

@celery.task
def get_submissions(subreddit_name, limit=50):
    gen  = r.get_subreddit(subreddit_name).get_top(limit=limit)
    return [sub._json_data for sub in gen]
