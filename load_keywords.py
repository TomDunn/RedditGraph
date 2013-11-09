from models.SubredditKeyword import SubredditKeyword
from db import Session

session = Session()
session.query(SubredditKeyword).delete()
session.commit()

with open('data/Keywords.csv') as f:
    for line in f:
        splitted = line.split(';')
        subreddit_id = splitted[0]

        for keyword_tfidf in splitted[1:]:
            keyword, tfidf = keyword_tfidf.split(' ')
            sw = SubredditKeyword.create(keyword, tfidf, subreddit_id)
            session.add(sw)

        session.commit()
