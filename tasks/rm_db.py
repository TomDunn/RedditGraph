from db import Base, engine
from models.Subreddit import Subreddit
from models.Community import Community
from models.SubredditCommunityAssociation import association_table
from models.DiscoveredSub import DiscoveredSub
from models.Post import Post
from models.User import User
from models.UserMeta import UserMeta
from models.UserPostVote import UserPostVote
from models.Comment import Comment
from models.UserLock import UserLock

def main(notify):
    Base.metadata.drop_all(bind=engine)
