from sqlalchemy import Column, String, SmallInteger, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence

from db import Base
from models.User import User
from models.Post import Post
from models.Util import Util

class UserPostVote(Base):
    __tablename__ = 'user_post_votes'

    id   = Column(Integer, Sequence('user_post_votes_seq'), unique=True, primary_key=True)
    vote = Column(Integer)

    post_id = Column(Integer, ForeignKey('posts.id'))
    post    = relationship('Post')

    user_id = Column(Integer, ForeignKey('users.id'))
    user    = relationship('User')

    @classmethod
    def create(cls, session, user, post, vote):
        inst = cls()

        inst.post_id = post.id
        inst.user_id = user.id
        inst.vote    = vote

        Util.add_and_refresh(session, inst)
        return inst

    @classmethod
    def get_or_create(cls, session, user, post, vote):
        vote = session.query(cls).filter(cls.post_id == post.id, cls.user_id == user.id).first()

        if vote == None:
            vote = cls.create(session, user, post, vote)

        return vote
