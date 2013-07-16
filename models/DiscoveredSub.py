from sqlalchemy import Column, String
from db import Base

class DiscoveredSub(Base):
    __tablename__ = 'discovered_subreddits'

    url    = Column(String, unique=True, primary_key=True)
    status = Column(String, default='NONE')
