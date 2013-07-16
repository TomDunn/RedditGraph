from sqlalchemy import Column, Integer, String, Boolean, Sequence
from sqlalchemy.orm import relationship

from db import Base
from models.Subreddit import Subreddit
from models.SubredditCommunityAssociation import association_table

class Community(Base):
    __tablename__ = 'communities'

    id = Column(Integer, Sequence('community_id_sequence'), primary_key=True)
    name = Column(String, default="Collection of subreddits")
    description = Column(String, default="Empty")

    subreddits = relationship("Subreddit", secondary=association_table, backref="communities")
