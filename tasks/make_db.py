from db import Base, engine
from models.Subreddit import Subreddit
from models.Community import Community
from models.SubredditCommunityAssociation import association_table
from models.DiscoveredSub import DiscoveredSub
from models.WikiEntry import WikiEntry
from models.Post import Post
from models.User import User
from models.UserPostVote import UserPostVote
from models.Comment import Comment

def main(notify):
    Base.metadata.create_all(engine)
