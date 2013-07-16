import networkx as nx

from db import Session
from models.Subreddit import Subreddit
from models.Community import Community
from models.SubredditCommunityAssociation import association_table
from tasks.coalesce_communities import get_coalesced_communities

def main():

    # read in the graph
    g  = nx.read_gexf('data/subreddits_edged_by_description_links.gexf')
    # create session
    session = Session()

    # clean out existing associations and communities
    for c in session.query(Community):
        c.subreddits[:] = []
    session.commit()

    session.query(Community).delete()

    communities = get_coalesced_communities(g)
    for c in communities:
        comm = Community()
        comm.name = "test"
        comm.description = ', '.join(c.members)

        make_url = lambda url: u'/r/' + url + u'/'
        urls = map(make_url, c.members)

        for sub in session.query(Subreddit).filter(Subreddit.url.in_(urls)):
            comm.subreddits.append(sub)

        session.add(comm)
        #session.commit()

    # commit the new communities
    session.commit()

    print "there are %d communities" % session.query(Community).count()
