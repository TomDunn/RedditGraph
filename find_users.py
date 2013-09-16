import praw
from sqlalchemy import func

from db import Session
from helpers.RFactory import r
from models.Post import Post
from models.User import User
from models.Comment import Comment

session = Session()

for comment in session.query(Comment).filter(Comment.check_author == True):
    res = session.query(User).filter(func.lower(User.name) == func.lower(comment.author_id)).first()

    if res == None:
        res = User()
        res.update_from_praw(r.get_redditor(comment.author_id))
        session.add(res)

    comment.author_id       = res.id
    comment.check_author    = False
    session.add(comment)
    session.commit()

for post in session.query(Post).filter(Post.check_author == True):
    res = session.query(User).filter(func.lower(User.name) == func.lower(post.author_id)).first()

    if res == None:
        res = User()
        res.update_from_praw(r.get_redditor(post.author_id))
        session.add(res)

    post.check_author   = False
    post.author_id      = res.id
    session.add(post)
    session.commit()

for user in session.query(User).filter(User.has_public_likes == 0):
    try:
        for post in r.get_redditor(user.name).get_liked(limit=1):
            user.has_public_likes = 1

    except praw.requests.exceptions.HTTPError:
        user.has_public_likes = 2

    session.merge(user)
    session.commit()
