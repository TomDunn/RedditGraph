from sqlalchemy import Column, Integer, String, Table, ForeignKey
from db import Base

association_table = Table('sc_association', Base.metadata,
        Column('community_id', Integer, ForeignKey('communities.id')),
        Column('subreddit_id', String,  ForeignKey('subreddits.id'))
)
