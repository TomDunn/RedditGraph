import time

from pydispatch import dispatcher
from sqlalchemy import Column, Integer, String, Boolean, Float, SmallInteger, ForeignKey
from sqlalchemy.schema import Sequence

from db import Base
from models.Util import Util

class User(Base):
    __tablename__ = 'users'

    id          = Column(Integer, Sequence('users_seq'), unique=True, primary_key=True)
    reddit_id   = Column(String)
    name        = Column(String, unique=True, primary_key=True)

    created      = Column(Float)
    created_utc  = Column(Float)
    scraped_time = Column(Float)

    link_karma      = Column(Integer)
    comment_karma   = Column(Integer)

    over_18 = Column(Boolean)
    is_gold = Column(Boolean)
    is_mod  = Column(Boolean)
    has_verified_email = Column(Boolean)

    # Signals
    CREATED_SIGNAL = 'USER_CREATED'

    @classmethod
    def create(cls, session, username):
        user        = cls()
        user.name   = username

        Util.add_and_refresh(session, user)
        dispatcher.send(signal=cls.CREATED_SIGNAL, sender=user)

        return user

    def update_from_json(self, j):
        self.reddit_id  = j['id']
        self.name       = j['name']

        self.created        = j['created']
        self.created_utc    = j['created_utc']
        self.scraped_time   = Util.now()

        self.link_karma     = j['link_karma']
        self.comment_karma  = j['comment_karma']

        self.over_18    = j['over_18']
        self.is_gold    = j['is_gold']
        self.is_mod     = j['is_mod']
        self.has_verified_email = j['has_verified_email']

    def update_from_praw(self, p):
        self.reddit_id  = p.id
        self.name       = p.name

        self.created        = p.created
        self.created_utc    = p.created_utc
        self.scraped_time   = time.mktime(time.gmtime())

        self.link_karma     = p.link_karma
        self.comment_karma  = p.comment_karma

        self.over_18    = p.over_18
        self.is_gold    = p.is_gold
        self.is_mod     = p.is_mod
        self.has_verified_email = p.has_verified_email

    @classmethod
    def get_or_create(cls, session, username):
        user = session.query(cls).filter(cls.name == username).first()

        if (user == None):
            user = User.create(session, username)

        return user
