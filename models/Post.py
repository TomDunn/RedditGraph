import time

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence

from db import Base
from models.Subreddit import Subreddit
from models.User import User
from models.Util import Util

class Post(Base):
    __tablename__ = 'posts'

    id          = Column(Integer, Sequence('posts_seq'), unique=True, primary_key=True)
    reddit_id   = Column(String, unique=True, primary_key=True)

    domain      = Column(String)
    url         = Column(String)
    permalink   = Column(String)

    selftext_html   = Column(String)
    selftext        = Column(String)
    title           = Column(String)
    thumbnail       = Column(String)

    author_id    = Column(Integer, ForeignKey('users.id'))
    author       = relationship('User')

    subreddit_id = Column(Integer, ForeignKey('subreddits.id'))
    subreddit    = relationship('Subreddit')
    edited       = Column(Float)

    score   = Column(Integer)
    downs   = Column(Integer)
    ups     = Column(Integer)

    over_18         = Column(Boolean)
    is_self         = Column(Boolean)
    num_comments    = Column(String)

    created         = Column(Float)
    created_utc     = Column(Float)
    scraped_time    = Column(Float)

    @classmethod
    def create(cls, session, post_id):
        post = cls()
        post.reddit_id = Util.plain_id(post_id)

        Util.add_and_refresh(session, post)
        return post

    def update_from_praw(self, p):
        self.domain = p.domain
        self.url    = p.url.lower().strip()
        self.permalink = p.permalink

        self.selftext_html  = p.selftext_html
        self.selftext       = p.selftext
        self.title          = p.title
        self.thumbnail      = p.thumbnail

        self.edited         = float(p.edited)
        self.reddit_id      = p.id

        self.score  = p.score
        self.downs  = p.downs
        self.ups    = p.ups

        self.over_18        = p.over_18
        self.is_self        = p.is_self
        self.num_comments   = p.num_comments

        self.created        = p.created
        self.created_utc    = p.created_utc
        self.scraped_time   = Util.now()

    @classmethod
    def get_or_create(cls, session, post_id):
        post_id = Util.plain_id(post_id)
        post = session.query(cls).filter(cls.reddit_id == post_id).first()

        if (post == None):
            post = cls.create(session, post_id)

        return post
