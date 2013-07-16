from flask import Flask, render_template

from db import Session
from models.Subreddit import Subreddit
from models.Community import Community

app = Flask(__name__)
app.debug = True

@app.route('/')
def default():
    return render_template('page_layout.html')

@app.route('/connected/<subreddit>')
def get_connected_subreddits(subreddit):
    s = Session()
    subreddit = s.query(Subreddit).filter(Subreddit.url == '/r/' + subreddit.lower() + '/').one()

    seen = set()
    subs = list()

    for c in subreddit.communities:
        for sub in c.subreddits:
            if sub.id not in seen:
                seen.add(sub.id)
                subs.append(sub)

    return render_template('list.html', subreddits = subs)

@app.route('/graph')
def show_community_graph():
    return render_template('community_graph.html')
