import praw

from db import Session
from models.Post import Post
from models.Subreddit import Subreddit
from models.User import User
from models.UserMeta import UserMeta
from models.UserPostVote import UserPostVote as Vote
from models.Util import Util
from helpers.RFactory import r

def update(session, user, praw_post, score):
    post = Post.get_or_create(session, praw_post.id)
    post.update_from_praw(praw_post)
    post.author_id = user.id
    Util.update_subreddit(Subreddit, post, session, praw_post.subreddit.display_name)
    vote = Vote.get_or_create(session, user, post, score)
    vote.vote = score

    session.add(vote)
    session.add(post)

session = Session()
gen = session.query(User) \
    .join(UserMeta) \
    .filter(User.reddit_id != None, \
        UserMeta.has_public_likes == UserMeta.YES, \
        UserMeta.is_active != UserMeta.NO)

for user in gen:
    try:
        praw_user = r.get_redditor(user.name)
        user.update_from_praw(praw_user)

        for praw_post in praw_user.get_liked(limit=100):
            update(session, user, praw_post, 1)

        for praw_post in praw_user.get_disliked(limit=100):
            update(session, user, praw_post, -1)

        user.meta.has_public_likes = UserMeta.YES
    except praw.requests.exceptions.HTTPError as e:
        print str(e)
        if '403' in str(e):
            user.meta.has_public_likes = UserMeta.NO
        elif '404' in str(e):
            user.meta.is_active = UserMeta.NO

    session.add(user.meta)
    session.add(user)
    session.commit()

session.close()
