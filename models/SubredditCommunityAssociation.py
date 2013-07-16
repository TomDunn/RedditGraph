from sqlalchemy import Column, Integer, String, Table, ForeignKey
from db import Base

association_table = Table('sc_association', Base.metadata,
        Column('community_id', Integer, ForeignKey('communities.id')),
        Column('subreddit_id', String,  ForeignKey('subreddits.id'))
)

"""
    class SubredditCommunityAssociation(Base):
        __tablename__ = 'subredditcommunityassociations'

        subreddit_id = Column(String, ForeignKey('subreddits.id'), primary_key = True)
        community_id = Column(Integer, ForeignKey('communities.id'), primary_key = True)

        community = relationship("Community")
        subreddit = relationship("Subreddit")
"""
