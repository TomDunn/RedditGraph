#!/usr/bin/env python2.7

from    __future__ import division
import  sqlite3
import  networkx as nx
from    Submission import Submission
from    util       import initialize_node

def main():
    db = sqlite3.connect('data/submissions.sqlite')
    g  = nx.Graph()

    for row in db.execute('SELECT * FROM submissions'):
        submission = Submission(row)
        from_sub = submission.subreddit.lower()

        initialize_node(g, from_sub)
        g.node[from_sub]['post_count'] += 1

        # weighten edges
        if submission.is_x_post():
            to_sub   = submission.get_sub_from_url().lower()
            initialize_node(g, to_sub)

            g.node[from_sub]['x_post_count']    += 1
            g.node[to_sub]['x_post_to_count']   += 1

            if g.has_edge(from_sub, to_sub):
                g[from_sub][to_sub]['weight'] += 1
            else:
                g.add_edge(from_sub, to_sub, weight=1)

        # keep track of self posts
        if submission.is_self_post():
            g.node[from_sub]['self_count'] += 1

    """
        Now I want to remove reddits who primarily link to
        other content on reddit (z.B. x-post reddits like bestof and worstof)

        And also remove nodes that are relatively weakly linked, I.E. degree of 1 or 0
    """

    # remove nodes (subs) that are x-post too heavily (>40%) 
    # or those whose weighted degree is less than a certain number
    to_remove = []
    for n in g:
        data = g.node[n]
        removed = False

        # avoid division by zero in the next if-block
        if data['post_count'] == 0: data['post_count'] = 1

        # the too heavy x-posters
        if data['x_post_count'] / data['post_count'] > .2:
            print "%s removed" % n
            to_remove.append(n)
            removed = True

        # the low weights
        weight = 0
        for e in g.edges(n, data=True):
            weight += e[2]['weight']

        if weight < 15 and not removed:
            print "%s for low weight" % n
            to_remove.append(n)

    # now remove them
    # TODO do better than this
    for n in to_remove:
        g.remove_node(n)

    db.close()
    nx.write_gexf(g, 'data/output.gexf')

if __name__ == "__main__":
    main()
