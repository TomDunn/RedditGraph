from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence

from db import Base
from models.Post import Post

class UserVoteBasedPostSimilarities(Base):
    __tablename__ = 'user_vote_based_post_similarities'

    id = Column(Integer, Sequence('uvbps_seq'), unique=True, primary_key=True)
    
    post_id1    = Column(Integer, ForeignKey('posts.id'))
    post_id2    = Column(Integer, ForeignKey('posts.id'))

    post1       = relationship(Post, primaryjoin=post_id1==Post.id)
    post2       = relationship(Post, primaryjoin=post_id2==Post.id)
    
    intersect   = Column(Integer)
    similarity  = Column(Float)
