import time

from sqlalchemy import Column, Integer, String, Boolean, Float, SmallInteger

from db import Base

class User(Base):
    __tablename__ = 'users'

    id   = Column(String, unique=True, primary_key=True)
    name = Column(String)

    created      = Column(Float)
    created_utc  = Column(Float)
    scraped_time = Column(Float)

    link_karma      = Column(Integer)
    comment_karma   = Column(Integer)

    over_18 = Column(Boolean)
    is_gold = Column(Boolean)
    is_mod  = Column(Boolean)
    has_verified_email = Column(Boolean)

    # 0 = unknown, 1 = yes, 2 = no
    has_public_likes = Column(SmallInteger, default = 0)
    active           = Column(SmallInteger)

    def update_from_praw(self, p):
        self.id     = p.id
        self.name   = p.name

        self.created        = p.created
        self.created_utc    = p.created_utc
        self.scraped_time   = time.mktime(time.gmtime())

        self.link_karma     = p.link_karma
        self.comment_karma  = p.comment_karma

        self.over_18    = p.over_18
        self.is_gold    = p.is_gold
        self.is_mod     = p.is_mod
        self.has_verified_email = p.has_verified_email

    def activate(self):
        self.active = 1

    def deactivate(self):
        self.active = 0
