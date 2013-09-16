import time

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from db import Base
from models.User import User
from models.Post import Post

class Comment(Base):
    __tablename__ = 'comments'

    id          = Column(String, unique=True, primary_key=True)

    parent_id   = Column(String, ForeignKey('comments.id'))
    parent      = relationship('Comment')

    gilded = Column(Boolean)
    edited = Column(Boolean)

    author_id       = Column(String, ForeignKey('users.id'))
    check_author    = Column(Boolean, default = True)
    author          = relationship('User')

    post_id = Column(String, ForeignKey('posts.id'))
    post    = relationship('Post')

    body    = Column(String)
    ups     = Column(Integer)
    downs   = Column(Integer)

    created         = Column(Float)
    created_utc     = Column(Float)
    scraped_time    = Column(Float)

    def update_from_praw(self, p):
        self.id = p.id

        self.parent_id = p.parent_id.split('_')[1]

        self.gilded = p.gilded
        self.edited = p.edited

        self.body   = p.body
        self.ups    = p.ups
        self.downs  = p.downs

        self.created        = p.created
        self.created_utc    = p.created_utc
        self.scraped_time   = time.mktime(time.gmtime())

        self.author_id      = p.author.name
        self.check_author   = True

        self.post_id = p.link_id.split('_')[1]
