from time import time

from celery import group
import praw

from db import Session
from helpers.RFactory import r
from models.Util import Util
from models.Comment import Comment
from models.Post import Post
from models.User import User
from models.Subreddit import Subreddit
from tasks.config.celery import celery
from tasks.get_subreddits import get_subreddit
from tasks.get_posts import get_submissions
from tasks.get_comments import get_comments

@celery.task
def crawl(subreddit_name):
    res = get_subreddit(subreddit_name)

    if res.get('invalid') or not res.get('value'):
        return res

    subreddit = res.get('value')

    submissions = get_submissions(subreddit_name, limit=50)
    comments    = get_comments(submissions)

    res = dict()
    res.update({
        'value': {'subreddit': subreddit, 'submissions': submissions, 'comments': comments}
    })

    return res

def main(notify):
    session = Session()
    gen = session.query(Subreddit.display_name) \
        .order_by(Subreddit.scraped_time) \
        .limit(500)

    names = map(lambda n: n[0], gen)
    task_group = group(crawl.s(n) for n in names)
    result     = task_group.apply_async()

    for res in result.iterate():
        handle_crawl_result(session, res)
        session.commit()

def handle_crawl_result(session, res):
    print time()
    if not res.get('value'):
        return

    display_name = res.get('value').get('subreddit').get('display_name')
    subreddit = Subreddit.get_or_create(session, display_name)

    if res.get('invalid'):
        subreddit.mark_invalid()
        return session.add(subreddit)

    praw_subreddit = praw.objects.Subreddit(r, json_dict=res.get('value').get('subreddit'))
    subreddit.update_from_praw(praw_subreddit)
    session.add(subreddit)

    submissions = res.get('value').get('submissions') 
    praw_submissions = map(lambda s: praw.objects.Submission(r, json_dict=s), submissions)
    submissions = []

    for praw_submission in praw_submissions:
        submission = Post.get_or_create(session, praw_submission.id)
        submission.update_from_praw(praw_submission)
        author = User.get_or_create(session, Util.patch_author(praw_submission.author))
        submission.author_id = author.id
        submission.subreddit_id = subreddit.id
        session.add(submission)
        session.add(author)
        submissions.append(submission)

    comments = res.get('value').get('comments')
    praw_comments = map(lambda c: praw.objects.Comment(r, json_dict=c), comments)

    for praw_comment in praw_comments:
        submission = filter(lambda s: s.reddit_id == Util.plain_id(praw_comment.link_id), submissions)[0]
        author = User.get_or_create(session, Util.patch_author(praw_comment.author))
        comment = Comment.get_or_create(session, praw_comment.id)
        comment.author_id = author.id
        comment.post_id = submission.id
        comment.update_from_praw(praw_comment)
        session.add(comment)
        session.add(author)

    print time()
    print '\n'
