from db import Session
from models.Subreddit import Subreddit as Sub
from models.DiscoveredSub import DiscoveredSub as DSub
from models.User import User
from models.UserMeta import UserMeta
from models.UserLock import UserLock
from models.Post import Post
from helpers.DBIterator import DBIterator as DBI

s = Session()
DI = DBI
Sub = Sub
DSub = DSub
P = Post
U = User
L = UserLock
M = UserMeta
