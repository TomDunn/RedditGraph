import time

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from db import Base
from models.Subreddit import Subreddit
from models.User import User

class Post(Base):
    __tablename__ = 'posts'

    id = Column(String, unique=True, primary_key=True)

    domain      = Column(String)
    url         = Column(String)
    permalink   = Column(String)

    selftext_html   = Column(String)
    selftext        = Column(String)
    title           = Column(String)
    thumbnail       = Column(String)

    author_id   = Column(String, ForeignKey('users.id'))
    author      = relationship('User')
    subreddit_id= Column(String, ForeignKey('subreddits.id'))
    subreddit   = relationship('Subreddit')
    edited      = Column(Float)

    score   = Column(Integer)
    downs   = Column(Integer)
    ups     = Column(Integer)

    over_18         = Column(Boolean)
    is_self         = Column(Boolean)
    num_comments    = Column(String)

    created         = Column(Float)
    created_utc     = Column(Float)
    scraped_time    = Column(Float)

    def update_from_praw(self, p):
        self.id = p.id

        self.domain = p.domain
        self.url    = p.url.lower().strip()
        self.permalink = p.permalink

        self.selftext_html  = p.selftext_html
        self.selftext       = p.selftext
        self.title          = p.title
        self.thumbnail      = p.thumbnail

        if p.author is not None:
            self.author_id      = p.author.name

        self.subreddit_id   = p.subreddit_id.split('_')[1]
        self.edited         = float(p.edited)

        self.score  = p.score
        self.downs  = p.downs
        self.ups    = p.ups

        self.over_18        = p.over_18
        self.is_self        = p.is_self
        self.num_comments   = p.num_comments

        self.created        = p.created
        self.created_utc    = p.created_utc
        self.scraped_time   = time.mktime(time.gmtime())
