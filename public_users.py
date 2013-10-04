import praw

from db import Session
from models.Post import Post
from models.User import User, UserMeta
from models.UserPostVote import UserPostVote as Vote
from helpers.RFactory import r

session = Session()

for user in session.query(User).join(UserMeta).filter(User.reddit_id != None, UserMeta.has_public_likes == UserMeta.UNKNOWN).limit(500):
    praw_user = r.get_redditor(user.name)

    try:
        for praw_post in praw_user.get_liked(limit=1000):
            post = Post.get_or_create(session, praw_post.id)
            vote = Vote.get_or_create(session, user, post, 1)

        user.meta.has_public_likes = user.meta.YES
    except praw.requests.exceptions.HTTPError as e:
        if '403' in e:
            user.meta.has_public_likes = user.meta.NO

    session.add(user.meta)
    session.commit()

session.close()
