from __future__ import absolute_import

from celery import group
import praw
from praw.helpers import flatten_tree

from db import Session
from helpers.RFactory import r
from models.Comment import Comment
from models.Post import Post
from models.User import User
from models.Subreddit import Subreddit
from models.Util import Util
from tasks.config.celery import celery

@celery.task
def get_comments(submissions, top=40):
    submissions = map(lambda s: praw.objects.Submission(r, json_dict=s), submissions)
    comments    = []

    for submission in submissions:
        for comment in flatten_tree(submission.comments):
            if not isinstance(comment, praw.objects.Comment):
                continue

            comment._json_data['replies'] = None
            comments.append(comment._json_data)

    return comments
