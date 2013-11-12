import time

from sqlalchemy import Column, Integer, String, Boolean, Float, func
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
    display_name        = Column(String, unique=True, primary_key=True, nullable=False)

    title   = Column(String)
    url     = Column(String, unique=True)

    name    = Column(String)
    id      = Column(Integer, Sequence('subreddits_seq'), unique=True, primary_key=True)
    reddit_id = Column(String, unique=True, default = None, nullable = True)

    created     = Column(Float)
    created_utc = Column(Float)
    scraped_time= Column(Float)

    accounts_active = Column(Integer)
    subscribers     = Column(Integer)
    over18          = Column(Boolean)

    @classmethod
    def create(cls, session, display_name):
        sub = cls()
        sub.display_name    = display_name

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
        self.scraped_time   = Util.now()

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
    def get_or_create(cls, session, display_name):
        sub = session.query(cls) \
            .filter(func.lower(cls.display_name) == func.lower(display_name)) \
            .first()
        
        if (sub == None):
            sub = cls.create(session, display_name)

        return sub

    @staticmethod
    def get_invalid_text():
        return '<INVALID>'

    def mark_invalid(self):
        self.display_name = self.get_invalid_text()
