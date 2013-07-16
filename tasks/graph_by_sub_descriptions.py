#!/usr/bin/env python2.7

import re
import json
from HTMLParser import HTMLParser

import networkx as nx
from BeautifulSoup import BeautifulSoup

from helpers.util import find_sub_links, initialize_node
from db import Session
from models.Subreddit import Subreddit

def main(notify):

    g = nx.Graph()
    out_filename = 'data/subreddits_edged_by_description_links.gexf'
    parser = HTMLParser()
    session = Session()

    for subreddit in session.query(Subreddit):
        sub = subreddit.url.split('/')[2].lower()

        initialize_node(g,sub)

        if not subreddit.description_html:
            continue

        html = parser.unescape(subreddit.description_html)
        for linked_sub in find_sub_links(html):
            if g.has_edge(sub, linked_sub):
                g[sub][linked_sub]['weight'] += 1
            else:
                g.add_edge(sub, linked_sub, weight=1)

    nx.write_gexf(g, out_filename)

if __name__ == "__main__":
    main()
