import time

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence

from db import Base
from models.User import User
from models.Post import Post
from models.Util import Util

class Comment(Base):
    __tablename__ = 'comments'

    id        = Column(Integer, Sequence('comments_seq'), unique=True, primary_key=True)
    reddit_id = Column(String, primary_key=True, unique=True)

    parent_id = Column(Integer, ForeignKey('comments.id'))
    parent    = relationship('Comment')

    gilded = Column(Boolean)
    edited = Column(Float)

    author_id = Column(Integer, ForeignKey('users.id'))
    author    = relationship('User')

    post_id = Column(Integer, ForeignKey('posts.id'))
    post    = relationship('Post')

    body  = Column(String)
    ups   = Column(Integer)
    downs = Column(Integer)

    created      = Column(Float)
    created_utc  = Column(Float)
    scraped_time = Column(Float)

    @classmethod
    def create(cls, session, comment_id):
        comment = cls()
        comment.reddit_id = Util.plain_id(comment_id)

        Util.add_and_refresh(session, comment)
        return comment

    @classmethod
    def get_or_create(cls, session, comment_id):
        comment_id = Util.plain_id(comment_id)
        comment = session.query(cls).filter(cls.reddit_id == comment_id).first()

        if (comment == None):
            comment = cls.create(session, comment_id)

        return comment

    def update_from_praw(self, p):
        self.reddit_id  = Util.plain_id(p.id)

        self.gilded = bool(p.gilded)
        self.edited = float(p.edited)

        self.body   = p.body
        self.ups    = p.ups
        self.downs  = p.downs

        self.created        = p.created
        self.created_utc    = p.created_utc
        self.scraped_time   = time.mktime(time.gmtime())
