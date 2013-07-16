from db import Base, engine
from models.Subreddit import Subreddit
from models.Community import Community
from models.SubredditCommunityAssociation import association_table
from models.DiscoveredSub import DiscoveredSub
from models.WikiEntry import WikiEntry

def main():
    Base.metadata.create_all(engine)
