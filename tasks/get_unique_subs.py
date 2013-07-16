#!/usr/bin/env python2.7

import  sqlite3
from    Submission import Submission

def main():
    db = sqlite3.connect('data/submissions.sqlite')
    subs = set()

    for row in db.execute('SELECT * FROM submissions'):
        submission = Submission(row)
        subs.add(submission.subreddit.lower())

    f = open('data/all_subreddits.txt', 'w')
    f.write('\n'.join(subs) + '\n')
    f.close()
