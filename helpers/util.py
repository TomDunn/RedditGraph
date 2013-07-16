from __future__ import division
from BeautifulSoup import BeautifulSoup
from networkx import find_cliques

def initialize_node(g, node):
    if node not in g:
        g.add_node(node)
        g.node[node]['post_count']      = 0
        g.node[node]['x_post_count']    = 0
        g.node[node]['self_count']      = 0
        g.node[node]['x_post_to_count'] = 0

"""
    Ugly but it works
"""
def find_sub_links(text):
    subs = set()
    for link in BeautifulSoup(text).findAll('a'):
        href =  link.get('href')
        try:
            splitted = href.split('/')
            index = splitted.index('r')
            if ('reddit.com' in href or href[0:3] == '/r/') and index + 1 < len(href):
                for s in splitted[index+1].lower().split('+'):
                    subs.add(s)
        except ValueError as e:
            #print "ERROR", href, e
            continue

    return subs

def average_clique_size(g):
    clique_sizes = map(lambda c: len(c), filter(lambda c: len(c) > 3, find_cliques(g)))
    return sum(clique_sizes) / len(clique_sizes)
