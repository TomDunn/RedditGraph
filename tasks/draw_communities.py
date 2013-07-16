from itertools import product
from random import choice
import networkx as nx
from helpers.colors import colors
from tasks.coalesce_communities import get_coalesced_communities

def make_node_id(prefix, node_name):
    return str(prefix) + '_' + node_name

def split_node_id(node_id):
    splitted = node_id.split('_')
    if len(splitted) != 2:
        print "NODE ID %s has %d components" % (node_id, len(splitted))
    return splitted

def expand_node(prefixes, g, node):
    names = set()

    for p in prefixes:
        name = make_node_id(p, node)
        if name in g:
            names.add(name)

    return names

def main(notify=None):

    if notify is None:
        notify = lambda s: s

    g  = nx.read_gexf('data/subreddits_edged_by_description_links.gexf')
    g1 = nx.Graph()

    notify("drawing a community graph for %d subreddits" % len(g))

    communities = get_coalesced_communities(g, no_overlap=True)
    all_members = set()
    duplicated = set()

    for c in communities:
        color = choice(colors)
        for n in c.members:
            if n in all_members:
                duplicated.add(n)
            all_members.add(n)
            node_id = make_node_id(c.id, n)
            g1.add_node(node_id)
            g1.node[node_id]['label'] = n
            g1.node[node_id]['viz'] = color

    print "members of nodes in communities is %d" % len(all_members)
    print "number of duplicated nodes %d" % len(duplicated)

    prefixes = set(map(lambda c: c.id, communities))
    prefixes.add('none')

    for edge in g.edges_iter(data=True):
        froms = expand_node(prefixes, g1, edge[0])
        tos   = expand_node(prefixes, g1, edge[1])

        w = edge[2]['weight']
        for from_node, to_node in product(froms, tos):
            g1.add_edge(from_node, to_node)
            g1[from_node][to_node]['weight'] = w

    to_remove = set()
    for node in g1:
        if g1.degree(node) == 0:
            to_remove.add(node)

    for node in to_remove:
        g1.remove_node(node)

    to_remove = list()
    for edge in g1.edges_iter(data=True):
        source = edge[0]
        target = edge[1]

        if source[36:] == target[36:]:
            to_remove.append(edge)

        if source[0:35] == target[0:35]:
            edge[2]['weight'] = edge[2]['weight'] * 20

    for edge in to_remove:
        g1.remove_edge(edge[0], edge[1])

    nx.write_gexf(g1, 'data/communities.gexf')

if __name__ == '__main__':
    main()
