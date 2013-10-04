import time

from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.schema import Sequence

from db import Base
from models.Util import Util

class Subreddit(Base):
    __tablename__ = 'subreddits'

    header_title    = Column(String)
    header_img      = Column(String)

    description_html    = Column(String)
    description         = Column(String)
    public_description  = Column(String)
    display_name        = Column(String)

    title   = Column(String)
    url     = Column(String, unique=True)

    name    = Column(String)
    id      = Column(Integer, Sequence('subreddits_seq'), unique=True, primary_key=True)
    reddit_id = Column(String, primary_key=True, unique=True)

    created     = Column(Float)
    created_utc = Column(Float)
    scraped_time= Column(Float)

    accounts_active = Column(Integer)
    subscribers     = Column(Integer)
    over18          = Column(Boolean)

    @classmethod
    def create(cls, session, subreddit_id):
        sub = cls()
        sub.reddit_id = Util.plain_id(subreddit_id)

        Util.add_and_refresh(session, sub)
        return sub

    def update_from_praw(self, p):
        self.header_img     = p.header_img
        self.header_title   = p.header_title
        self.title          = p.title
        self.display_name   = p.display_name

        self.name   = p.name
        self.url    = p.url.lower().strip()

        self.reddit_id = Util.plain_id(p.id)

        self.description        = p.description
        self.description_html   = p.description_html
        self.public_description = p.public_description

        self.created        = p.created
        self.created_utc    = p.created_utc
        self.scraped_time   = time.mktime(time.gmtime())

        self.accounts_active = p.accounts_active
        self.subscribers = p.subscribers
        self.over18 = bool(p.over18)

    def touch(self):
        self.scraped_time = Util.now()

    def url_to_name(self):
        return self.url.split('/')[2]

    @classmethod
    def make_url(cls, subreddit_name):
        return u'/r/' + subreddit_name + '/'

    @classmethod
    def get_or_create(cls, session, subreddit_id):
        subreddit_id = Util.plain_id(subreddit_id)
        sub = session.query(cls).filter(cls.reddit_id == subreddit_id).first()
        
        if (sub == None):
            sub = cls.create(session, subreddit_id)

        return sub
