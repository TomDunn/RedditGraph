from celery import group

from tasks.config.celery import celery
from tasks.get_subreddits import get_subreddit
from tasks.get_posts import get_submissions
from tasks.get_comments import get_comments

@celery.task
def crawl(subreddit_name):
    subreddit = get_subreddit(subreddit_name)

    if not subreddit:
        return None

    submissions = get_submissions(subreddit_name)
    comments    = get_comments(submissions)

    return {
        'subreddit':    subreddit,
        'submissions':  submissions,
        'comments':     comments
    }

def main(notify):
    task_group = group(crawl.s(n) for n in ['python', 'programming', 'compsci'])
    result     = task_group.apply_async()

    for res in result.iterate():
        if not res:
            print "non-existant subreddit"
            continue

        print res['subreddit']['display_name']
