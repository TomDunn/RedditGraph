import praw

from db import Session
from helpers.RFactory import r
from models.User import User
from models.UserPostVote import UserPostVote

session = Session()

for user in session.query(User).filter(User.has_public_likes == 1):
    try:
        for post in r.get_redditor(user.name).get_liked(limit=1):
            vote = session.merge(UserPostVote.create(user, post, 1))

    except praw.request.exceptions.HTTPError as e:
        if '403' in e:
            user.has_public_likes = 2
            session.add(user)

    session.commit()
