from itertools import product
from random import choice

import networkx as nx

from helpers.colors import colors
from tasks.coalesce_communities import get_coalesced_communities

def main(notify=None):

    if notify is None:
        notify = lambda s: s

    g  = nx.read_gexf('data/subreddits_edged_by_description_links.gexf')
    g1 = nx.Graph()

    notify("drawing a community graph for %d subreddits" % len(g))

    communities = filter(lambda c: len(c.members) > 0, get_coalesced_communities(g, no_overlap=True))
    all_members = set()

    for c in communities:
        color = choice(colors)
        for n in c.members:

            all_members.add(n)
            g1.add_node(n)
            g1.node[n]['label'] = n
            g1.node[n]['comm_id'] = str(c.id)
            g1.node[n]['viz'] = color

    notify("number of nodes in communities is %d" % len(all_members))

    for edge in g.edges_iter(data=True):
        source, target, data = edge
        weight = data['weight']

        if source == target:
            continue

        if source in g1 and target in g1:
            g1.add_edge(source, target)
            g1[source][target]['weight'] = weight

    for edge in g1.edges_iter(data=True):
        source = g1.node[edge[0]]
        target = g1.node[edge[1]]

        if source['comm_id'] == target['comm_id']:
            edge[2]['weight'] = edge[2]['weight'] * 10
        if edge[0] not in g1 or edge[1] not in g1:
            print edge[0], edge[1]
            print edge[0] in g1, edge[1] in g1
            print "-----"
    nx.write_gexf(g1, 'data/communities.gexf')
