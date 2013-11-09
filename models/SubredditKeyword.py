from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence

from db import Base
from models.Subreddit import Subreddit

class SubredditKeyword(Base):
    __tablename__ = 'subreddit_keywords'

    id = Column(Integer, Sequence('subreddit_keywords_seq'), unique=True, primary_key=True)

    subreddit_id = Column(Integer, ForeignKey('subreddits.id'))
    subreddit    = relationship('Subreddit')

    keyword = Column(String)
    tfidf   = Column(Float)

    @classmethod
    def create(cls, keyword, tfidf, subreddit_id):
        inst = cls()

        inst.keyword      = keyword
        inst.tfidf        = tfidf
        inst.subreddit_id = subreddit_id

        return inst
