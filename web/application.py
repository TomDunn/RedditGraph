import json
from uuid import uuid4

from flask import Flask, render_template, jsonify, request

from db import Session
from models.Subreddit import Subreddit
from models.Community import Community
from models.User import User
from models.UserLock import UserLock

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
    usernames = [user['name'] for user in users]

    for lock in session.query(UserLock).join(User) \
        .filter(User.name.in_(usernames), UserLock.status == UserLock.STATUS_WIP, UserLock.locker == worker):
        for u in users:
            if u['name'] == lock.user.name:
                if 'error' in u:
                    eId = str(uuid4())
                    print "ERROR:", eId
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
