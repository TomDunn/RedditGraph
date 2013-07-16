import json
from db import Session
from models.Subreddit import Subreddit

session = Session()
in_filename = 'data/subreddits_about.json'
count = 0

for line in open(in_filename):
    try:

        d = json.loads(line)
        s = Subreddit()
        
        s.header_img    = d['header_img']
        s.header_title  = d['header_title']

        s.description       = d['description']
        s.description_html  = d['description_html']
        s.public_description= d['public_description']

        s.title = d['title']
        s.url   = d['url'].lower().strip()

        s.created       = d['created']
        s.created_utc   = d['created_utc']
        s.scraped_time  = d['scraped_time']

        s.id    = d['id']
        s.name  = d['name']

        s.over18            = bool(d['over18'])
        s.subscribers       = d['subscribers']
        s.accounts_active   = d['accounts_active']
        s.display_name      = d['display_name']

        session.add(s)
        count += 1

        if count % 25 == 0:
            session.commit()


    except ValueError as e:
        print "ERROR", e
        continue

session.commit()
