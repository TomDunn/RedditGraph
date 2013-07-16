from db import Session
from models.Subreddit import Subreddit as Sub
from models.DiscoveredSub import DiscoveredSub as DSub

s = Session()
Sub = Sub
DSub = DSub
