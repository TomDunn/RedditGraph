from sqlalchemy import Column, String, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship

from db import Base
from models.User import User
from models.Post import Post

class UserPostVote(Base):
    __tablename__ = 'user_post_votes'

    id = Column(String, unique=True, primary_key=True)
    vote = Column(SmallInteger, default=0)

    post_id = Column(String, ForeignKey('posts.id'))
    post    = relationship('Post')

    user_id = Column(String, ForeignKey('users.id'))
    user    = relationship('User')

    @classmethod
    def create(cls, user, post, vote = 0):
        inst = cls()

        inst.post_id = post.id
        inst.user_id = user.id
        inst.vote    = vote
        inst.id      = UserPostVote.make_id(user, post)

        return inst

    @staticmethod
    def make_id(user, post):
        return user.id + '_' + post.id
