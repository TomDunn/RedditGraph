from time import time
from json import dumps

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
    res = get_subreddit(display_name=subreddit_name)

    if res.get('invalid'):
        return res

    subreddit   = res.get('value').get('subreddit')
    submissions = get_submissions(display_name=subreddit_name, limit=20)

    comments = None
    
    if submissions is None:
        res.update({'invalid': True})
    else:
        comments = get_comments(submissions=submissions)

    res = dict()
    res.update({'value': {'subreddit': subreddit, 'submissions': submissions, 'comments': comments}})

    return res

def main(notify):
    session = Session()
    gen = session.query(Subreddit.display_name) \
        .filter(Subreddit.name != Subreddit.get_invalid_text()) \
        .order_by(Subreddit.scraped_time) \
        .limit(10)

    names = map(lambda n: n[0], gen)
    task_group = group(crawl.s(n) for n in names)
    result     = task_group.apply_async()

    session.close()
    count = 0

    for res in result.iterate():
        start = time()
        print start

        name = res.get('value').get('subreddit').get('display_name')

        subreddit = Subreddit.get_or_create(session, name)
        subreddit.touch()

        if res.get('invalid'):
            subreddit.mark_invalid()

        session.add(subreddit)
        session.commit()

        if res.get('invalid'):
            continue

        fname = "data/crawls/%s_%s.json" % (name, str(int(time())))
        save_to_file(fname, res)
        print time() - start, '\n'

def save_to_file(fname, result):
    with open(fname, 'wb') as f:
        f.write(dumps(result) + '\n')

def handle_crawl_result(session, res):
    start = time()
    print start
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

    print len(praw_comments)
    print time() - start

    praw_comments = sorted(praw_comments, key=lambda c: c.ups - c.downs, reverse=True)
    print map(lambda c: c.ups - c.downs, praw_comments[0:10])

    for praw_comment in praw_comments[0:400]:
        submission = filter(lambda s: s.reddit_id == Util.plain_id(praw_comment.link_id), submissions)[0]
        author = User.get_or_create(session, Util.patch_author(praw_comment.author))
        comment = Comment.get_or_create(session, praw_comment.id)
        comment.author_id = author.id
        comment.post_id = submission.id
        comment.update_from_praw(praw_comment)
        session.add(comment)
        session.add(author)

    print time() - start
    print '\n'
