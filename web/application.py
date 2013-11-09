import json
from uuid import uuid4
import pprint

from flask import Flask, render_template, jsonify, request
from sqlalchemy.orm import aliased
from sqlalchemy import or_, func

from db import Session
from models.Subreddit import Subreddit
from models.Community import Community
from models.Post import Post
from models.User import User
from models.UserLock import UserLock
from models.UserVoteBasedPostSimilarities import UserVoteBasedPostSimilarities as UVBPS
from models.SubredditKeyword import SubredditKeyword
from models.Util import Util

app = Flask(__name__)
app.debug = True

@app.route('/')
def default():
    return render_template('page_layout.html')

@app.route('/uvbps')
def uvbps():
    session = Session()

    post_alias = aliased(Post)

    gen = session.query(UVBPS) \
        .filter(UVBPS.intersect >= 5) \
        .join(UVBPS.post1) \
        .join(post_alias, UVBPS.post1) \
        .filter(or_(Post.score <= 1000, post_alias.score <= 1000)) \
        .order_by(UVBPS.intersect.desc()) \
        .limit(500)
    return render_template('uvbps.html', gen=gen)

@app.route('/subreddit_keywords')
def subreddit_keywords():
    session = Session()

    subreddit_name = request.args.get('subreddit', 'python')
    gen = session.query(SubredditKeyword) \
        .join(Subreddit) \
        .filter(func.lower(Subreddit.display_name) == func.lower(subreddit_name))

    return render_template('subreddit_keywords.html', gen=gen)

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

@app.route('/new_users', methods=['POST'])
def new_users():
    users = json.loads(request.data)
    users = users['users']
    session = Session()

    for user in users:
        User.get_or_create_temp(session, user)

    return jsonify({'received': 'true'})

@app.route('/get_id')
def get_id():
    return jsonify({'id': str(uuid4())})

@app.route('/make_batch', methods=['POST'])
def make_batch():
    session = Session()
    data = json.loads(request.data)
    worker = data['id']

    if UserLock.get_locked(session, worker).count() < 10:
        UserLock.lock(session, worker)
        session.commit()

    users = []

    for locked in UserLock.get_locked(session, worker):
        users.append(locked.user.name)

    session.close()
    return jsonify({'users': users})

@app.route('/put_batch', methods=['PUT'])
def put_batch():
    session = Session()
    data = json.loads(request.data)
    worker = data['id']
    users  = data['users']
    users = filter(lambda u: u is not None, users)
    usernames = [user['name'] for user in users]

    for lock in session.query(UserLock).join(User) \
        .filter(User.name.in_(usernames), UserLock.status == UserLock.STATUS_WIP, UserLock.locker == worker):
        for u in users:
            if u['name'] == lock.user.name:
                if 'error' in u:
                    eId = str(uuid4())
                    lock.user.reddit_id = eId
                else:
                    lock.user.update_from_json(u)
                session.add(lock.user)

    session.commit()

    session.query(UserLock).join(User) \
        .filter(User.reddit_id != None, User.name.in_(usernames), UserLock.status == UserLock.STATUS_WIP, UserLock.locker == worker) \
        .update({'status': UserLock.STATUS_DONE, 'locker': None}, synchronize_session='fetch')

    session.commit()
    session.close()

    return jsonify({'received':'true'})

@app.route('/links', methods=['POST'])
def post_links():
    session = Session()
    data = json.loads(request.data)

    for link in data['links']:
        post = Post.get_or_create(session, link['reddit_id'])
        subreddit = Subreddit.get_or_create(session, link['sub_name'])
        user = User.get_or_create(session, link['authorname'])

        post.subreddit_id   = subreddit.id
        post.author_id      = user.id

        post.domain = link['domain']
        post.title  = link['title']
        post.url    = link['url']
        post.score  = link['score']
        post.downs  = link['downs']
        post.ups    = link['ups']

        post.is_self = link['is_self']
        post.over_18 = link['over_18']
        post.thumbnail = link['thumbnail']
        post.created = float(link['created'])
        post.scraped_time = Util.now()

        session.add(post)

    session.commit()
    session.close()
    return jsonify({'received':True})
