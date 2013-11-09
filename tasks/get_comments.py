import praw
from praw.helpers import flatten_tree
from sqlalchemy.orm.exc import NoResultFound

from db import Session
from models.Comment import Comment
from models.Post import Post
from models.User import User
from models.Subreddit import Subreddit
from models.Util import Util
from helpers.RFactory import r

def main(notify):
    session = Session()

    subreddit_names = set()

    for sub in session.query(Post.subreddit_id).distinct():
        try:
            sub = session.query(Subreddit).filter(Subreddit.id == sub[0]).one()
            subreddit_names.add(sub.display_name)
        except NoResultFound:
            print "none found"

    subreddit_names = filter(lambda n: n != None and len(n) > 0, subreddit_names)

    count = session.query(Comment).count()
    notify("Starting w/ %d" % count)

    for name in subreddit_names:
        try:
            praw_subreddit = r.get_subreddit(name)
            for praw_submission in praw_subreddit.get_hot(limit=40):
                for praw_comment in flatten_tree(praw_submission.comments):

                    if not isinstance(praw_comment, praw.objects.Comment):
                        continue

                    count += 1

                    comment = Comment.get_or_create(session, praw_comment.id)
                    comment.update_from_praw(praw_comment)

                    author_name = Util.patch_author(praw_comment.author)
                    user = User.get_or_create(session, author_name)
                    post = Post.get_or_create(session, praw_comment.link_id)

                    subreddit = Subreddit.get_or_create(session, praw_comment.subreddit.display_name);
                    subreddit.update_from_praw(praw_subreddit)

                    post.update_from_praw(praw_submission)
                    post.subreddit_id = subreddit.id

                    comment.author_id   = user.id
                    comment.post_id     = post.id

                    session.add(comment)
                    session.add(post)
                    session.add(subreddit)

                session.commit()

        except praw.requests.exceptions.HTTPError:
            continue
        except praw.errors.InvalidSubreddit:
            continue

    notify("Ending w/ %d" % count)
