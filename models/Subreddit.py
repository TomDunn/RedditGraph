import time

from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship

from db import Base
from models.WikiEntry import WikiEntry

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
    id      = Column(String, unique=True, primary_key=True)

    created     = Column(Float)
    created_utc = Column(Float)
    scraped_time= Column(Float)

    accounts_active = Column(Integer)
    subscribers     = Column(Integer)
    over18          = Column(Boolean)

    # relationships
    wiki_pages      = relationship("WikiEntry", backref="subreddit")

    def update_from_praw(self, p):

        self.header_img     = p.header_img
        self.header_title   = p.header_title
        self.title          = p.title
        self.display_name   = p.display_name

        self.name   = p.name
        self.url    = p.url.lower().strip()
        self.id     = p.id

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
        self.scraped_time = time.mktime(time.gmtime())
