#!/usr/bin/env python2.7

from __future__ import division
from itertools import product

import networkx as nx
from helpers.Community import Community
from helpers.util import average_clique_size as get_average_clique_size

def coalesce_communities(communities, min_overlap):

    # calculate best matches for communities to be coalesced to
    for c1,c2 in product(communities, communities):
        if c1.members <= c2.members and c2.members <= c1.members:
            continue

        if c1.size > c2.size:
            continue

        intersect = c1.members & c2.members
        ratio = len(intersect) / c1.size

        if ratio > min_overlap and ratio > c1.best_match_weight:
            c1.best_match = c2
            c1.best_match_weight = ratio

    # update 
    for c in filter(lambda com: com.best_match is not None, communities):
        c.best_match.best_match_for.add(c.id)

    # coalesce
    while True:

        for c in filter(lambda com: com.best_match is not None and len(com.best_match_for) == 0, communities):
            c.best_match.members.update(c.members)
            c.best_match.update_name()
            c.best_match.best_match_for.discard(c.id)

            c.members.clear()
            c.update_name()

        coalesced = filter(lambda x: not len(x.members) == 0, communities)
        if len(coalesced) == len(communities):
            break

        communities = coalesced

    return communities

def get_coalesced_communities(g):

    average_clique_size = int(get_average_clique_size(g))
    communities = map(lambda c: Community(c), nx.k_clique_communities(g, average_clique_size))
    communities = coalesce_communities(communities, .7)

    communities2 = map(lambda c: Community(c), nx.k_clique_communities(g, 3))
    communities2 = coalesce_communities(communities2, .7)

    communities = communities + filter(lambda c: len(c.members) <= 10, communities2)
    communities = coalesce_communities(communities, .7)
    communities = filter(lambda c: len(c.members) > 1, communities)

    print 'finished coalescion'
    return communities

def main():
    # the description link graph
    g = nx.read_gexf('data/subreddits_edged_by_description_links.gexf')

    # an empty graph for showing communities
    g1 = nx.Graph()

    communities = get_coalesced_communities(g)
    for c in communities:
        g1.add_node(c.name)
        g1.node[c.name]['size'] = len(c.members)

    count = 0
    ratio_weight = 0.0

    for c1, c2 in product(communities, communities):
        if c1.id == c2.id or g1.has_edge(c1.name, c2.name) or len(c1.members) > len(c2.members):
            continue
        
        overlap = len(c1.members & c2.members)

        if overlap > 0:
            g1.add_edge(c1.name, c2.name, weight=overlap / len(c1.members))
            ratio_weight += overlap / len(c1.members)
            count += 1

    average_weight_ratio = ratio_weight / count
    print "average weight ratio: %s" % str(average_weight_ratio)

    g1.remove_edges_from(filter(lambda x: x[2]['weight'] < average_weight_ratio, g1.edges(data=True)))

    print "%d subreddits included" % len(reduce(lambda x,y: x.union(y.members), communities, set()))
    nx.write_gexf(g1, 'test_coalesce.gexf')
