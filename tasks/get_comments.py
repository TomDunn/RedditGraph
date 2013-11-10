from __future__ import absolute_import

from celery import group
import praw
from praw.helpers import flatten_tree
from sqlalchemy.orm.exc import NoResultFound

from db import Session
from helpers.JSONObject import JSONObject
from helpers.RFactory import r
from models.Comment import Comment
from models.Post import Post
from models.User import User
from models.Subreddit import Subreddit
from models.Util import Util
from tasks.config.celery import celery

def main(notify):
    session = Session()

    subreddit_names = set()

    gen = session.query(Subreddit) \
        .filter(Subreddit.display_name != Subreddit.get_invalid_text()) \
        .order_by(Subreddit.scraped_time) \
        .limit(100)

    for subreddit in gen:
        print subreddit.display_name
        subreddit_names.add(subreddit.display_name)

    task_group = group(run.s(name,top=30) for name in subreddit_names)
    results = task_group.apply_async()

    for result in results.iterate():
        if type(result) in [str, unicode]:
            print "NONE", '\n'
            subreddit = session.query(Subreddit).filter(Subreddit.display_name == result).one()
            subreddit.mark_invalid()
            session.add(subreddit)
            session.commit()
            continue

        update(session, result)

def update(session, result):
    print result['subreddit']['display_name']
    praw_subreddit = JSONObject(**result['subreddit'])
    subreddit = Subreddit.get_or_create(session, praw_subreddit.display_name)
    subreddit.update_from_praw(praw_subreddit)
    session.add(subreddit)
    
    for submission_comments in result['submissions']:
        praw_submission, comments = submission_comments
        praw_submission = JSONObject(**praw_submission)

        post = Post.get_or_create(session, praw_submission.id)
        post.update_from_praw(praw_submission)

        post_author = User.get_or_create(session, praw_submission.author)
        post.author_id = post_author.id
        session.add(post)

        for praw_comment in comments:
            praw_comment = JSONObject(**praw_comment)
            comment = Comment.get_or_create(session, praw_comment.id)
            comment.update_from_praw(praw_comment)
            comment.post_id = post.id

            author = User.get_or_create(session, praw_comment.author)
            comment.author_id = author.id
            session.add(comment)

    session.commit()

@celery.task
def run(name, top=40):
    try:
        submissions = []
        praw_subreddit = r.get_subreddit(name)

        for praw_submission in praw_subreddit.get_hot(limit=top):
            comments = []

            for praw_comment in flatten_tree(praw_submission.comments):

                if not isinstance(praw_comment, praw.objects.Comment):
                    continue

                praw_comment.__dict__['author'] = Util.patch_author(praw_comment.author)
                comments.append(JSONObject(**praw_comment.__dict__).json_safe_dict())

            # force submission to load
            praw_submission.title

            praw_submission.__dict__['author'] = Util.patch_author(praw_submission.author)
            submission = JSONObject(**praw_submission.__dict__).json_safe_dict()

            submissions.append((submission, comments))

        # force subreddit to load via praw
        praw_subreddit.title

        praw_subreddit = JSONObject(**praw_subreddit.__dict__).json_safe_dict()
        return {'subreddit': praw_subreddit, 'submissions':  submissions}

    except praw.errors.InvalidSubreddit:
        return name
    except praw.requests.exceptions.HTTPError as e:
        if '404' in str(e) or '403' in str(e):
            return name
        else:
            return ''
