from db import Session
from models.User import User
from helpers.RFactory import r

import praw

session = Session()
count = 0

for u in session.query(User).filter(User.created != None):
    user = r.get_redditor(u.name)

    try:
        for p in user.get_liked():
            print p.title
        count += 1
    except praw.requests.exceptions.HTTPError:
        pass

print count
