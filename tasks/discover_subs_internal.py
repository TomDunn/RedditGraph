import praw
from HTMLParser import HTMLParser

from db import Session
from models.Subreddit import Subreddit
from models.DiscoveredSub import DiscoveredSub
from helpers.util import find_sub_links

def add_new_subs(session, subs):
    print subs
    for url in subs:
        s = DiscoveredSub()
        s.url = url
        session.add(s)
    session.commit()
    subs.clear()

def main():
    parser = HTMLParser()
    session = Session()

    starting_count = session.query(Subreddit).count()
    discovered_subs = set()

    for sub in session.query(Subreddit.description_html).filter(Subreddit.description_html != None):
        links = set(map(lambda s: u'/r/' + s.lower().strip() + u'/', find_sub_links(parser.unescape(sub.description_html))))

        if len(links) == 0:
            continue

        existing = set(map(lambda s: s.url.lower().strip(), session.query(Subreddit.url).filter(Subreddit.url.in_(links))))
        found    = set(map(lambda s: s.url.lower().strip(), session.query(DiscoveredSub.url).filter(DiscoveredSub.url.in_(links))))
        new_subs = (links - existing) - found

        if len(new_subs) > 0:
            discovered_subs.update(new_subs)

        if len(discovered_subs) > 25:
            add_new_subs(session, discovered_subs)

    if len(discovered_subs) > 0:
        add_new_subs(session, discovered_subs)

    end_count = session.query(DiscoveredSub).count()
    print "started with: %d, found %d" % (starting_count, end_count)

if __name__=='__main__':
    main()
